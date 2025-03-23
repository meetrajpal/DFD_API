import os
import shutil
from sqlalchemy.orm import Session
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
import torch
import cv2
from torchvision.models.video import mvit_v2_s
from torch.nn import functional as F
from dto.res.ErrorResDto import ErrorResDto
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from services.DetectService import DetectService
from services.impl.VideoServiceImpl import VideoServiceImpl


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_PATH = os.path.join("model", "mvit_random_multi_dataset.pth")
INPUT_SIZE = (224, 224)
CLIP_LENGTH = 16


def load_model():
    model = mvit_v2_s(weights=None)
    model.head = torch.nn.Sequential(
        torch.nn.Dropout(0.5),
        torch.nn.Linear(model.head[-1].in_features, 2)
    )
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    model.to(DEVICE).eval()
    return model


model = load_model()


def preprocess_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, INPUT_SIZE)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = torch.tensor(frame, dtype=torch.float32).permute(2, 0, 1) / 255.0
        frames.append(frame)

    cap.release()

    while len(frames) < CLIP_LENGTH:
        frames.append(frames[-1] if frames else torch.zeros(3, *INPUT_SIZE))

    frames = frames[:CLIP_LENGTH]
    frames = torch.stack(frames, dim=1)
    frames = frames.unsqueeze(0).to(DEVICE)

    return frames


class DetectServiceImpl(DetectService):

    def __init__(self, db: Session):
        self.db = db

    def detect_video(self, user_id: int, username: str, file: UploadFile = File(...)):

        file_path = os.path.join(os.getenv("UPLOAD_DIR"), f"{username}_{file.filename}")

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            return JSONResponse(content=GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="internal_server_error",
                    message="Failed to save video file.",
                    details=str(e),
                ),
                message="Error occurred while saving the video."
            ).dict(), status_code=500)

        video_service = VideoServiceImpl(self.db)
        new_video = video_service.add_video(f"{username}_{file.filename}", file_path, user_id)

        if isinstance(new_video, JSONResponse):
            return new_video

        input_tensor = preprocess_video(file_path)

        with torch.no_grad():
            output = model(input_tensor)
            probabilities = F.softmax(output, dim=1)
            confidence, predicted_class = torch.max(probabilities, 1)

        result = "FAKE" if predicted_class.item() == 1 else "REAL"
        confidence_score = f"{confidence.item():.2f}"

        if os.path.exists(file_path):
            os.remove(file_path)

        return JSONResponse(content=GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message=f"Detection Result: {result} (Confidence: {confidence_score})."
        ).dict(), status_code=200)

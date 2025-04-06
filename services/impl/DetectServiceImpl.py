import os
import cv2
import torch
import httpx
import shutil
import numpy as np
from torch.amp import autocast
from facenet_pytorch import MTCNN
from sqlalchemy.orm import Session
from torchvision import transforms
from fastapi import UploadFile, File
from torch.nn import functional as F
from fastapi.responses import JSONResponse
from urllib.parse import urlparse, parse_qs
from dto.res.ErrorResDto import ErrorResDto
from torchvision.models.video import mvit_v2_s
from services.DetectService import DetectService
from dto.res.GeneralMsgResDto import GeneralMsgResDto
from services.impl.VideoServiceImpl import VideoServiceImpl
from services.impl.PredictionServiceImpl import PredictionServiceImpl

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_PATH = os.path.join("trained_model", "best_multi_6k_allaugs_mvit_mtcnn.pth")
INPUT_SIZE = (224, 224)
CLIP_LENGTH = 16

face_detector = MTCNN(image_size=INPUT_SIZE[0], margin=20, keep_all=False, device=DEVICE)

# Define transforms consistent with training
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize(INPUT_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.45, 0.45, 0.45], std=[0.225, 0.225, 0.225])  # Match training normalization
])


def get_youtube_video_id(url):
    parsed_url = urlparse(url)
    if "youtube.com" in parsed_url.netloc:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif "youtu.be" in parsed_url.netloc:
        return parsed_url.path.lstrip('/')
    return None


def get_facebook_share_id(url):
    parsed_url = urlparse(url)
    unique_id = parsed_url.path.strip('/').split('/')[-1]
    return unique_id


# Model class consistent with training
class MViTForDeepfakes(torch.nn.Module):
    def __init__(self, num_classes=2):
        super().__init__()
        self.backbone = mvit_v2_s(weights="DEFAULT")  # Use pretrained weights as in training
        self.backbone.head = torch.nn.Sequential(
            torch.nn.Dropout(0.5),
            torch.nn.Linear(self.backbone.head[-1].in_features, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)


# Load model with proper checkpoint handling
model = MViTForDeepfakes()
checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)

# Extract state_dict from checkpoint (training saved it as a dict with 'model_state_dict')
if 'model_state_dict' in checkpoint:
    state_dict = checkpoint['model_state_dict']
else:
    state_dict = checkpoint

# Remove 'module.' prefix if present (due to DataParallel in training)
if list(state_dict.keys())[0].startswith("module."):
    state_dict = {k.replace("module.", ""): v for k, v in state_dict.items()}

model.load_state_dict(state_dict, strict=False)  # Use strict=False to handle potential mismatches

if torch.cuda.device_count() > 1:
    model = torch.nn.DataParallel(model)

model.to(DEVICE).eval()

allowed_extensions = {"mp4", "avi", "mov", "mkv"}


def preprocess_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame)
    cap.release()

    if len(frames) > CLIP_LENGTH:
        idxs = np.linspace(0, len(frames) - 1, CLIP_LENGTH, dtype=int)
        frames = [frames[i] for i in idxs]

    while len(frames) < CLIP_LENGTH:
        frames.append(frames[-1] if frames else np.zeros((*INPUT_SIZE, 3), dtype=np.uint8))

    processed_frames = []
    face_detected = False

    for frame in frames:
        face = face_detector(frame)
        if face is not None:
            face_detected = True
            face = face.permute(1, 2, 0).cpu().numpy()
        else:
            face = cv2.resize(frame, INPUT_SIZE)
        face_tensor = transform(face)
        processed_frames.append(face_tensor)

    if not face_detected:
        return None

    clip = torch.stack(processed_frames).permute(1, 0, 2, 3).unsqueeze(0).to(DEVICE)
    return clip


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
        new_video = video_service.add_video(f"{username}_{file.filename}", file_path, user_id, "direct upload", "NA")

        if isinstance(new_video, JSONResponse):
            return new_video

        input_tensor = preprocess_video(file_path)

        if input_tensor is None:
            if os.path.exists(file_path):
                os.remove(file_path)
            return JSONResponse(content=GeneralMsgResDto(
                isSuccess=False,
                hasException=False,
                message="Sorry, we are unable to detect sufficient face frames in the video. Please upload a different video."
            ).dict(), status_code=400)

        with torch.no_grad():
            with autocast(device_type='cuda', enabled=True):
                output = model(input_tensor)
            probabilities = F.softmax(output, dim=1)
            confidence, predicted_class = torch.max(probabilities, 1)

        result = "FAKE" if predicted_class.item() == 1 else "REAL"
        confidence_score = f"{(confidence.item()*100):.2f}"

        if os.path.exists(file_path):
            os.remove(file_path)

        prediction_service = PredictionServiceImpl(self.db)
        prediction_service.add_prediction(user_id, new_video.video_id, result)

        return JSONResponse(content=GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message=f"Detection Result: {result} (Confidence: {confidence_score}%)."
        ).dict(), status_code=200)

    async def ig_reel(self, user_id: int, username: str, url: str):
        callurl = f"https://instagram-reels-downloader-api.p.rapidapi.com/download?url={url}"
        headers = {
            "x-rapidapi-host": os.getenv("IG_H"),
            "x-rapidapi-key": os.getenv("RKEY")
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(callurl, headers=headers)
            if response:
                data = response.json()
            else:
                error_res = GeneralMsgResDto(
                    isSuccess=False,
                    hasException=True,
                    errorResDto=ErrorResDto(
                        code="internal_server_error",
                        message="No response from IG reel download server.",
                        details="No response from IG reel download server. Try after some time.",
                    ),
                    message="Error occurred while downloading the reel download server."
                )
                return JSONResponse(content=error_res.dict(), status_code=500)

        if data["data"]["medias"][0]["url"]:
            download_url = data["data"]["medias"][0]["url"]
            extension = data["data"]["medias"][0]["extension"]
            filename = f"{username}_{data["data"]["shortcode"]}.{extension}"
        else:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="We are unable to download this reel.",
                    details="We are unable to download this reel. Try with another reel.",
                ),
                message="Error occurred while downloading the reel download server."
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

        if extension not in allowed_extensions:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="bad_request",
                    message=f"The downloaded file has extension {extension} which is currently not supported.",
                    details=f"Only {allowed_extensions} are allowed",
                ),
                message="Request could not be completed due to an error."
            )
            return JSONResponse(content=error_res.dict(), status_code=400)

        file_path = os.path.join(os.getenv("UPLOAD_DIR"), filename)

        async with httpx.AsyncClient() as client:
            response = await client.get(download_url)
            if response.status_code == 200:
                with open(file_path, "wb") as file:
                    file.write(response.content)
            else:
                error_res = GeneralMsgResDto(
                    isSuccess=False,
                    hasException=True,
                    errorResDto=ErrorResDto(
                        code="not_found",
                        message="We are unable to save this reel on our server.",
                        details="We are unable to download this reel. Try with another reel.",
                    ),
                    message="Error occurred while downloading the reel download server."
                )
                return JSONResponse(content=error_res.dict(), status_code=500)

        video_service = VideoServiceImpl(self.db)
        new_video = video_service.add_video(filename, file_path, user_id, "instagram reel", url)

        if isinstance(new_video, JSONResponse):
            return new_video

        input_tensor = preprocess_video(file_path)

        if input_tensor is None:
            if os.path.exists(file_path):
                os.remove(file_path)
            return JSONResponse(content=GeneralMsgResDto(
                isSuccess=False,
                hasException=False,
                message="Sorry, we are unable to detect sufficient face frames in the video. Please upload a different video."
            ).dict(), status_code=400)

        with torch.no_grad():
            with autocast(device_type='cuda', enabled=True):
                output = model(input_tensor)
            probabilities = F.softmax(output, dim=1)
            confidence, predicted_class = torch.max(probabilities, 1)

        result = "FAKE" if predicted_class.item() == 1 else "REAL"
        confidence_score = f"{(confidence.item()*100):.2f}"

        if os.path.exists(file_path):
            os.remove(file_path)

        prediction_service = PredictionServiceImpl(self.db)
        prediction_service.add_prediction(user_id, new_video.video_id, result)

        return JSONResponse(content=GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message=f"Detection Result: {result} (Confidence: {confidence_score}%)."
        ).dict(), status_code=200)

    async def twitter_video(self, user_id: int, username: str, url: str):
        callurl = f"https://twitter-video-and-image-downloader.p.rapidapi.com/twitter?url={url}"
        headers = {
            "x-rapidapi-host": os.getenv("TWITTER_H"),
            "x-rapidapi-key": os.getenv("RKEY")
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(callurl, headers=headers)
            if response:
                data = response.json()
            else:
                error_res = GeneralMsgResDto(
                    isSuccess=False,
                    hasException=True,
                    errorResDto=ErrorResDto(
                        code="internal_server_error",
                        message="No response from Twitter video download server.",
                        details="No response from Twitter video download server. Try after some time.",
                    ),
                    message="Error occurred while downloading the Twitter video."
                )
                return JSONResponse(content=error_res.dict(), status_code=500)

        if data["media"][0]["url"]:
            download_url = data["media"][0]["url"]
            extension = "mp4"
            filename = f"{username}_{data["id"]}.{extension}"
        else:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="We are unable to download this Twitter video.",
                    details="We are unable to download this Twitter video. Try with another Twitter video.",
                ),
                message="Error occurred while downloading the Twitter video."
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

        file_path = os.path.join(os.getenv("UPLOAD_DIR"), filename)

        async with httpx.AsyncClient() as client:
            response = await client.get(download_url)
            if response.status_code == 200:
                with open(file_path, "wb") as file:
                    file.write(response.content)
            else:
                error_res = GeneralMsgResDto(
                    isSuccess=False,
                    hasException=True,
                    errorResDto=ErrorResDto(
                        code="not_found",
                        message="We are unable to save this Twitter video on our server.",
                        details="We are unable to download this Twitter video. Try with another Twitter video.",
                    ),
                    message="Error occurred while downloading the Twitter video."
                )
                return JSONResponse(content=error_res.dict(), status_code=500)

        video_service = VideoServiceImpl(self.db)
        new_video = video_service.add_video(filename, file_path, user_id, "twitter video", url)

        if isinstance(new_video, JSONResponse):
            return new_video

        input_tensor = preprocess_video(file_path)

        if input_tensor is None:
            if os.path.exists(file_path):
                os.remove(file_path)
            return JSONResponse(content=GeneralMsgResDto(
                isSuccess=False,
                hasException=False,
                message="Sorry, we are unable to detect sufficient face frames in the video. Please upload a different video."
            ).dict(), status_code=400)

        with torch.no_grad():
            with autocast(device_type='cuda', enabled=True):
                output = model(input_tensor)
            probabilities = F.softmax(output, dim=1)
            confidence, predicted_class = torch.max(probabilities, 1)

        result = "FAKE" if predicted_class.item() == 1 else "REAL"
        confidence_score = f"{(confidence.item()*100):.2f}"

        if os.path.exists(file_path):
            os.remove(file_path)

        prediction_service = PredictionServiceImpl(self.db)
        prediction_service.add_prediction(user_id, new_video.video_id, result)

        return JSONResponse(content=GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message=f"Detection Result: {result} (Confidence: {confidence_score}%)."
        ).dict(), status_code=200)

    async def youtube_video(self, user_id: int, username: str, url: str):
        callurl = f"https://social-download-all-in-one.p.rapidapi.com/v1/social/autolink"
        headers = {
            "x-rapidapi-host": os.getenv("YT_H"),
            "x-rapidapi-key": os.getenv("RKEY")
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(callurl, json={"url": url}, headers=headers)
            if response:
                data = response.json()
            else:
                error_res = GeneralMsgResDto(
                    isSuccess=False,
                    hasException=True,
                    errorResDto=ErrorResDto(
                        code="internal_server_error",
                        message="No response from YouTube video download server.",
                        details="No response from YouTube video download server. Try after some time.",
                    ),
                    message="Error occurred while downloading the YouTube video."
                )
                return JSONResponse(content=error_res.dict(), status_code=500)

        if data["medias"][0]["url"]:
            download_url = data["medias"][0]["url"]
            extension = data["medias"][0]["ext"]
            videoid = get_youtube_video_id(url)
            if videoid is None:
                error_res = GeneralMsgResDto(
                    isSuccess=False,
                    hasException=True,
                    errorResDto=ErrorResDto(
                        code="not_found",
                        message="We are unable to extract video id for this YouTube video.",
                        details="We are unable to extract video id for this YouTube video. Try with another YouTube video.",
                    ),
                    message="Request could not be completed due to an error."
                )
                return JSONResponse(content=error_res.dict(), status_code=500)
            filename = f"{username}_{videoid}.{extension}"
        else:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="We are unable to download this YouTube video.",
                    details="We are unable to download this YouTube video. Try with another YouTube video.",
                ),
                message="Error occurred while downloading the YouTube video."
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

        file_path = os.path.join(os.getenv("UPLOAD_DIR"), filename)

        async with httpx.AsyncClient() as client:
            response = await client.get(download_url)
            if response.status_code in (200, 302):  # Handle redirect or success
                with open(file_path, "wb") as file:
                    file.write(response.content)
            else:
                error_res = GeneralMsgResDto(
                    isSuccess=False,
                    hasException=True,
                    errorResDto=ErrorResDto(
                        code="not_found",
                        message="We are unable to save this YouTube video on our server.",
                        details="We are unable to download this YouTube video. Try with another YouTube video.",
                    ),
                    message="Error occurred while downloading the YouTube video."
                )
                return JSONResponse(content=error_res.dict(), status_code=500)

        video_service = VideoServiceImpl(self.db)
        new_video = video_service.add_video(filename, file_path, user_id, "youtube video", url)

        if isinstance(new_video, JSONResponse):
            return new_video

        input_tensor = preprocess_video(file_path)

        if input_tensor is None:
            if os.path.exists(file_path):
                os.remove(file_path)
            return JSONResponse(content=GeneralMsgResDto(
                isSuccess=False,
                hasException=False,
                message="Sorry, we are unable to detect sufficient face frames in the video. Please upload a different video."
            ).dict(), status_code=400)

        with torch.no_grad():
            with autocast(device_type='cuda', enabled=True):
                output = model(input_tensor)
            probabilities = F.softmax(output, dim=1)
            confidence, predicted_class = torch.max(probabilities, 1)

        result = "FAKE" if predicted_class.item() == 1 else "REAL"
        confidence_score = f"{(confidence.item()*100):.2f}"

        if os.path.exists(file_path):
            os.remove(file_path)

        prediction_service = PredictionServiceImpl(self.db)
        prediction_service.add_prediction(user_id, new_video.video_id, result)

        return JSONResponse(content=GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message=f"Detection Result: {result} (Confidence: {confidence_score}%)."
        ).dict(), status_code=200)

    async def facebook(self, user_id: int, username: str, url: str):
        callurl = f"https://social-download-all-in-one.p.rapidapi.com/v1/social/autolink"
        headers = {
            "x-rapidapi-host": os.getenv("YT_H"),
            "x-rapidapi-key": os.getenv("RKEY")
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(callurl, json={"url": url}, headers=headers)
            if response:
                data = response.json()
            else:
                error_res = GeneralMsgResDto(
                    isSuccess=False,
                    hasException=True,
                    errorResDto=ErrorResDto(
                        code="internal_server_error",
                        message="No response from Facebook video download server.",
                        details="No response from Facebook video download server. Try after some time.",
                    ),
                    message="Error occurred while downloading the Facebook video."
                )
                return JSONResponse(content=error_res.dict(), status_code=500)

        if data["medias"][0]["url"]:
            download_url = data["medias"][0]["url"]
            extension = data["medias"][0]["extension"]
            videoid = get_facebook_share_id(url)
            if videoid is None:
                error_res = GeneralMsgResDto(
                    isSuccess=False,
                    hasException=True,
                    errorResDto=ErrorResDto(
                        code="not_found",
                        message="We are unable to extract video id for this Facebook video.",
                        details="We are unable to extract video id for this Facebook video. Try with another Facebook video.",
                    ),
                    message="Request could not be completed due to an error."
                )
                return JSONResponse(content=error_res.dict(), status_code=500)
            filename = f"{username}_{videoid}.{extension}"
        else:
            error_res = GeneralMsgResDto(
                isSuccess=False,
                hasException=True,
                errorResDto=ErrorResDto(
                    code="not_found",
                    message="We are unable to download this Facebook video.",
                    details="We are unable to download this Facebook video. Try with another Facebook video.",
                ),
                message="Error occurred while downloading the Facebook video."
            )
            return JSONResponse(content=error_res.dict(), status_code=500)

        file_path = os.path.join(os.getenv("UPLOAD_DIR"), filename)

        async with httpx.AsyncClient() as client:
            response = await client.get(download_url)
            if response.status_code == 200:
                with open(file_path, "wb") as file:
                    file.write(response.content)
            else:
                error_res = GeneralMsgResDto(
                    isSuccess=False,
                    hasException=True,
                    errorResDto=ErrorResDto(
                        code="not_found",
                        message="We are unable to save this Facebook video on our server.",
                        details="We are unable to download this Facebook video. Try with another Facebook video.",
                    ),
                    message="Error occurred while downloading the Facebook video."
                )
                return JSONResponse(content=error_res.dict(), status_code=500)

        video_service = VideoServiceImpl(self.db)
        new_video = video_service.add_video(filename, file_path, user_id, "facebook video", url)

        if isinstance(new_video, JSONResponse):
            return new_video

        input_tensor = preprocess_video(file_path)

        if input_tensor is None:
            if os.path.exists(file_path):
                os.remove(file_path)
            return JSONResponse(content=GeneralMsgResDto(
                isSuccess=False,
                hasException=False,
                message="Sorry, we are unable to detect sufficient face frames in the video. Please upload a different video."
            ).dict(), status_code=400)

        with torch.no_grad():
            with autocast(device_type='cuda', enabled=True):
                output = model(input_tensor)
            probabilities = F.softmax(output, dim=1)
            confidence, predicted_class = torch.max(probabilities, 1)

        result = "FAKE" if predicted_class.item() == 1 else "REAL"
        confidence_score = f"{(confidence.item()*100):.2f}"

        if os.path.exists(file_path):
            os.remove(file_path)

        prediction_service = PredictionServiceImpl(self.db)
        prediction_service.add_prediction(user_id, new_video.video_id, result)

        return JSONResponse(content=GeneralMsgResDto(
            isSuccess=True,
            hasException=False,
            message=f"Detection Result: {result} (Confidence: {confidence_score}%)."
        ).dict(), status_code=200)

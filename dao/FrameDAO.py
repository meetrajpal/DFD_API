from sqlalchemy.orm import Session
from models.Frame import Frame
from operator import and_


class FrameDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_all_frames(self):
        return self.db.query(Frame).all()

    def get_frame_by_id(self, frame_id: int):
        return self.db.query(Frame).filter(Frame.frame_id == frame_id).first()

    def get_frame_by_videoid(self, video_id: int):
        return self.db.query(Frame).filter(Frame.video_id == video_id).first()

    def get_frames_by_userid(self, user_id: int):
        return self.db.query(Frame).filter(Frame.user_id == user_id).all()

    def get_frames_by_videoid_userid_filename(self, video_id: int, user_id: int, filename: str):
        return self.db.query(Frame).filter(Frame.user_id == user_id).filter(Frame.video_id == video_id).filter(Frame.filename == filename).first()

    def get_frame_by_multiple_filters(self, filters: list):
        return self.db.query(Frame).filter(and_(*filters)).all()

    def create_frame(self, frame: Frame):
        self.db.add(frame)
        self.db.commit()
        self.db.refresh(frame)
        return frame

    def delete_frame(self, frame: Frame):
        self.db.delete(frame)
        self.db.commit()

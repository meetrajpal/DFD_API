from sqlalchemy.orm import Session
from models.Video import Video
from operator import and_


class VideoDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_all_videos(self):
        return self.db.query(Video).all()

    def get_video_by_id(self, video_id: int):
        return self.db.query(Video).filter(Video.video_id == video_id).first()

    def get_videos_by_userid(self, user_id: int):
        return self.db.query(Video).filter(Video.user_id == user_id).all()

    def get_videos_by_userid_filename(self, user_id: int, filename: str):
        return self.db.query(Video).filter(Video.user_id == user_id).filter(Video.filename == filename).first()

    def get_video_by_multiple_filters(self, filters: list):
        return self.db.query(Video).filter(and_(*filters)).all()

    def create_video(self, video: Video):
        self.db.add(video)
        self.db.commit()
        self.db.refresh(video)
        return video

    def delete_video(self, video: Video):
        self.db.delete(video)
        self.db.commit()

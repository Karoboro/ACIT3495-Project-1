from sqlalchemy.orm import declarative_base, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


Base = declarative_base()


class VideoStreams(Base):
    __tablename__ = "video_streams"
    id = mapped_column(Integer, primary_key=True)
    description = mapped_column(String(250), nullable=False)
    url = mapped_column(String(500), nullable=False)
    user_id = mapped_column(ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="videos")
    upload_timestamp = mapped_column(DateTime, nullable=False,
                                     default=func.now())

    def to_dict(self):
        return {
            "description": self.description,
            "url": self.url,
            "uploader": self.user.username,
        }


class User(Base, UserMixin):
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(String(50), nullable=False, unique=True)
    password_hash = mapped_column(String(250), nullable=False)
    videos = relationship("VideoStreams", back_populates="user")
    created_timestamp = mapped_column(DateTime, nullable=False,
                                      default=func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

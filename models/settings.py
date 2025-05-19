from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class UserSettings(Base):
    __tablename__ = "UserSettings"

    user_id = Column(String, ForeignKey("User.id"), primary_key=True)

    default_source_lang = Column(String, default="en")
    default_target_lang = Column(String, default="zh")
    default_quiz_length = Column(Integer, default=10)
    daily_learning_goal = Column(Integer, default=10)
    auto_tts = Column(Boolean, default=True)
    reverse_quiz_default = Column(Boolean, default=False)
    dark_mode = Column(Boolean, default=False)
    onboarding_completed = Column(Boolean, default=False)

    user = relationship("User")
# conversation.py
from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid


class Conversation(Base):
    __tablename__ = "Conversation"
    __table_args__ = {"schema": "GenAIChatbot"}

    conversation_id = Column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )  # Add default UUID
    conversation_name = Column(String, default="New chat")  # Add default value
    soft_delete = Column(Boolean, default=False)

    workspace_id = Column(Integer, ForeignKey("GenAIChatbot.Workspace.workspace_id"))
    # user_id = Column(Integer, ForeignKey('GenAIChatbot.User.user_id'))
    user_id = Column(String(255), ForeignKey("GenAIChatbot.User.user_id"))

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    workspace = relationship("Workspace", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    responses = relationship("Response", back_populates="conversation")

    def __repr__(self):
        return f"<Conversation(conversation_id={self.conversation_id}, conversation_name={self.conversation_name})>"

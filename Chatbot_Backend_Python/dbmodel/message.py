# message.py
from sqlalchemy import Column, Text, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Message(Base):
    __tablename__ = "Message"
    __table_args__ = {"schema": "GenAIChatbot"}

    message_id = Column(
        Integer, primary_key=True, autoincrement=True
    )  # Ensure auto-increment
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False, default=0)
    status = Column(String, default="active")
    belongs_to_after_edit = Column(Integer)  # Add this column
    version = Column(Integer)  # Add this column
    sender_id = Column(String(255), ForeignKey("GenAIChatbot.User.user_id"))
    conversation_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("GenAIChatbot.Conversation.conversation_id"),
        nullable=False,
    )
    conversation = relationship("Conversation", back_populates="messages")
    senders = relationship("User", back_populates="messages")
    responses = relationship(
        "Response", back_populates="message", cascade="all, delete-orphan"
    )

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Message(message_id={self.message_id}, content={self.content}, status={self.status}, conversation_id={self.conversation_id})>"

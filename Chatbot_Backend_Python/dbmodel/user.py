from sqlalchemy import Column, String, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .base import Base


class User(Base):
    __tablename__ = "User"
    __table_args__ = {"schema": "GenAIChatbot"}

    # user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), primary_key=True)  # 255 is an example length

    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False)
    mobile = Column(String, nullable=False)
    organisation_id = Column(
        Integer, ForeignKey("GenAIChatbot.Organisation.organisation_id")
    )
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    # Define the relationship with Organisation
    organisation = relationship("Organisation", back_populates="users")
    workspaces_owned = relationship("Workspace", back_populates="owner")
    workspace_memberships = relationship("WorkspaceMember", back_populates="user")
    messages = relationship("Message", back_populates="senders")
    # Define the relationship with Conversation
    conversations = relationship("Conversation", back_populates="user")
    workspaces = relationship(
        "Workspace", back_populates="owner", overlaps="workspaces_owned"
    )

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"

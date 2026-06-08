from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid


class Workspace(Base):
    __tablename__ = "Workspace"
    __table_args__ = {"schema": "GenAIChatbot"}

    workspace_id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_name = Column(String, nullable=False)
    owner_id = Column(
        String(255), ForeignKey("GenAIChatbot.User.user_id")
    )  # Use UUID for foreign key
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    # Define relationships
    members = relationship(
        "WorkspaceMember",
        foreign_keys="WorkspaceMember.workspace_id",
        back_populates="workspace",
    )
    conversations = relationship(
        "Conversation",
        foreign_keys="Conversation.workspace_id",
        back_populates="workspace",
    )
    owner = relationship(
        "User", foreign_keys="Workspace.owner_id", back_populates="workspaces_owned"
    )

    def __repr__(self):
        return f"<Workspace(workspace_id={self.workspace_id}, workspace_name={self.workspace_name})>"

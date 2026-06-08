from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
import uuid


class WorkspaceMember(Base):
    __tablename__ = "WorkspaceMember"
    __table_args__ = {"schema": "GenAIChatbot"}

    member_id = Column(
        Integer, primary_key=True, autoincrement=True
    )  # Use UUID instead of Integer
    workspace_id = Column(
        Integer, ForeignKey("GenAIChatbot.Workspace.workspace_id")
    )  # Use UUID for foreign key
    user_id = Column(
        String(255), ForeignKey("GenAIChatbot.User.user_id")
    )  # Use UUID for foreign key
    status = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    # Define relationships
    user = relationship("User", back_populates="workspace_memberships")
    workspace = relationship("Workspace", back_populates="members")

    def __repr__(self):
        return f"<WorkspaceMember(member_id={self.member_id}, status={self.status})>"

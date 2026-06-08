from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Organisation(Base):
    __tablename__ = 'Organisation'
    __table_args__ = {'schema': 'GenAIChatbot'}
    organisation_id = Column(Integer, primary_key=True, autoincrement=True)
   
    organisation_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
   
    users = relationship('User', back_populates='organisation')
    def __repr__(self):
        return f"<Organisation(organisation_id={self.organisation_id}, name={self.organisation_name})>"
 
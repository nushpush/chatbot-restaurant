from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, DECIMAL, String, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Response(Base):
    __tablename__ = 'Response'
    __table_args__ = {'schema': 'GenAIChatbot'}
    
    response_id = Column(Integer, primary_key=True, autoincrement=True)
    response = Column(Text, nullable=False)
    vote = Column(Boolean)
    doc_ref = Column(ARRAY(String), nullable=True)  # Adjusted to use ARRAY type
    input_token = Column(Integer, nullable=True)
    output_token = Column(Integer, nullable=True)
    status = Column(String, default="active")
    version = Column(Integer, nullable=True)
    flesch_kincaid_grade_level = Column(DECIMAL, nullable=True)
    ari_grade_level = Column(DECIMAL, nullable=True)
    answer_similarity = Column(Integer, nullable=True)
    answer_correctness = Column(Integer, nullable=True)
    answer_relevance = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Foreign key relationship with Message and Conversation
    message_id = Column(Integer, ForeignKey('GenAIChatbot.Message.message_id'), nullable=False)
    message = relationship('Message', back_populates='responses')

    conversation_id = Column(PG_UUID(as_uuid=True), ForeignKey('GenAIChatbot.Conversation.conversation_id'), nullable=False)
    conversation = relationship('Conversation', back_populates='responses')

    def __repr__(self):
        return f"<Response(response_id={self.response_id}, response={self.response}, status={self.status})>"

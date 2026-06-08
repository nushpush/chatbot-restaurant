
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbmodel.base import Base
from dbmodel.conversation import Conversation
import uuid

# Example of test case for Conversation model
def test_create_conversation(session):
    # Create a new conversation object
    conversation = Conversation(
        conversation_name="Test Chat", 
        workspace_id=1, 
        user_id=1
    )
    
    # Add the conversation to the session and commit the transaction
    session.add(conversation)
    session.commit()

    # Fetch the conversation from the database
    result = session.query(Conversation).filter_by(conversation_name="Test Chat").first()

    # Assertions to verify that the conversation was created correctly
    assert result is not None  # Check that the conversation exists
    assert isinstance(result.conversation_id, uuid.UUID)  # Ensure conversation_id is a UUID
    assert result.conversation_name == "Test Chat"  # Verify conversation_name
    assert result.soft_delete == False  # Check default value for soft_delete
    assert result.workspace_id == 1  # Check workspace_id
    assert result.user_id == 1  # Check user_id
    assert result.created_at is not None  # Check that created_at is set
    assert result.updated_at is not None  # Check that updated_at is set

    # Test default values if no conversation_name provided
    default_conversation = Conversation(workspace_id=2, user_id=2)
    session.add(default_conversation)
    session.commit()

    # Fetch the default conversation
    default_result = session.query(Conversation).filter_by(workspace_id=2).first()
    
    assert default_result.conversation_name == "New chat"  # Check default value for conversation_name
    assert default_result.soft_delete == False  # Default soft_delete should be False


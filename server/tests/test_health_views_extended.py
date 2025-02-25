import pytest
from django.test import Client
from unittest.mock import patch
from core.models import ChatConversation
from django.db import OperationalError

@pytest.fixture
def client():
    return Client()

@pytest.mark.django_db
def test_health_check(client):
    """Test basic health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert data['message'] == 'Server is running'

@pytest.mark.django_db
def test_db_connection_success(client):
    """Test successful database connection check"""
    response = client.get('/api/health/db')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert data['message'] == 'Database connection successful'

@pytest.mark.django_db
def test_db_connection_error(client):
    """Test database connection error handling"""
    with patch.object(ChatConversation.objects, 'create', side_effect=OperationalError('Connection refused')):
        response = client.get('/api/health/db')
        assert response.status_code == 500
        data = response.json()
        assert data['status'] == 'error'
        assert 'Connection refused' in data['message']

@pytest.mark.django_db
def test_db_connection_other_error(client):
    """Test handling of other database errors"""
    with patch.object(ChatConversation.objects, 'create', side_effect=Exception('Unknown error')):
        response = client.get('/api/health/db')
        assert response.status_code == 500
        data = response.json()
        assert data['status'] == 'error'
        assert 'Unknown error' in data['message']

@pytest.mark.django_db
def test_db_connection_delete_error(client):
    """Test handling of errors during record deletion"""
    mock_record = ChatConversation()
    mock_record.delete = lambda: exec('raise Exception("Delete failed")')
    
    with patch.object(ChatConversation.objects, 'create', return_value=mock_record):
        response = client.get('/api/health/db')
        assert response.status_code == 500
        data = response.json()
        assert data['status'] == 'error'
        assert 'Delete failed' in data['message']

@pytest.mark.django_db
def test_chat_conversation_model():
    """Test ChatConversation model operations"""
    # Create test record
    conversation = ChatConversation.objects.create(
        session_id='test-session',
        conversation_history=[{'test': 'message'}]
    )
    
    # Verify creation
    assert conversation.session_id == 'test-session'
    assert len(conversation.conversation_history) == 1
    assert conversation.conversation_history[0]['test'] == 'message'
    
    # Clean up
    conversation.delete()

@pytest.mark.django_db
def test_chat_conversation_model_update():
    """Test updating ChatConversation model"""
    # Create test record
    conversation = ChatConversation.objects.create(
        session_id='test-session',
        conversation_history=[{'test': 'message'}]
    )
    
    # Update conversation history
    conversation.conversation_history.append({'test': 'message2'})
    conversation.save()
    
    # Verify update
    updated = ChatConversation.objects.get(session_id='test-session')
    assert len(updated.conversation_history) == 2
    assert updated.conversation_history[1]['test'] == 'message2'
    
    # Clean up
    conversation.delete()

@pytest.mark.django_db
def test_chat_conversation_model_delete():
    """Test deleting ChatConversation model"""
    # Create test record
    conversation = ChatConversation.objects.create(
        session_id='test-session',
        conversation_history=[{'test': 'message'}]
    )
    
    # Delete record
    conversation_id = conversation.id
    conversation.delete()
    
    # Verify deletion
    with pytest.raises(ChatConversation.DoesNotExist):
        ChatConversation.objects.get(id=conversation_id)

@pytest.mark.django_db
def test_chat_conversation_model_invalid():
    """Test invalid ChatConversation model operations"""
    with pytest.raises(Exception):
        ChatConversation.objects.create(
            session_id=None,  # Invalid: session_id is required
            conversation_history=[{'test': 'message'}]
        )

@pytest.mark.django_db
def test_chat_conversation_model_empty_history():
    """Test ChatConversation model with empty history"""
    conversation = ChatConversation.objects.create(
        session_id='test-session',
        conversation_history=[]
    )
    assert len(conversation.conversation_history) == 0
    conversation.delete()

@pytest.mark.django_db
def test_chat_conversation_model_large_history():
    """Test ChatConversation model with large conversation history"""
    large_history = [{'msg': f'test{i}'} for i in range(100)]
    conversation = ChatConversation.objects.create(
        session_id='test-session',
        conversation_history=large_history
    )
    assert len(conversation.conversation_history) == 100
    conversation.delete()

@pytest.mark.django_db
def test_chat_conversation_model_concurrent():
    """Test concurrent operations on ChatConversation model"""
    # Create multiple conversations
    conversations = []
    for i in range(5):
        conv = ChatConversation.objects.create(
            session_id=f'test-session-{i}',
            conversation_history=[{'test': f'message{i}'}]
        )
        conversations.append(conv)
    
    # Verify all were created
    assert ChatConversation.objects.count() >= 5
    
    # Clean up
    for conv in conversations:
        conv.delete()

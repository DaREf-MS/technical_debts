"""
Pytest configuration and fixtures for automatic test cleanup
"""
import pytest
from unit_tests.mock_app import init_mock_app
from src.models import db
from src.models.model import IdentifiableEntity
import uuid

@pytest.fixture(scope='session')
def app():
    """Create and configure a test Flask application"""
    app = init_mock_app()
    
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app"""
    return app.test_client()


@pytest.fixture(scope='function', autouse=True)
def cleanup_database(app):
    """
    Automatically cleanup database after each test
    This fixture runs before and after each test function
    """
    # Setup: runs before each test
    with app.app_context():
        # Start with clean database for each test
        db.drop_all()
        db.create_all()
    
    yield  # Test runs here
    
    # Teardown: runs after each test
    with app.app_context():
        # Clean up after the test
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='session', autouse=True)
def cleanup_session(app):
    """
    Cleanup database after entire test session and initialize default entities
    This ensures database is clean even if tests are interrupted
    """
    yield  # All tests run here
    
    # Final cleanup after all tests
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.create_all()
        
        # Add default identifiable entities
        todo_entity = IdentifiableEntity(id = str(uuid.uuid4()), name='TODO')
        fixme_entity = IdentifiableEntity(id = str(uuid.uuid4()), name='FIXME')
        
        db.session.add(todo_entity)
        db.session.add(fixme_entity)
        db.session.commit()

# students/tests/conftest.py

import pytest
from django.test import Client
from django.contrib.auth import get_user_model

@pytest.fixture
def authenticated_client(client):
    """
    Fixture to provide a Django test client that is logged in.
    """
    User = get_user_model()
    
    # Create a user for the tests, if not exists
    if not User.objects.filter(username='testuser').exists():
        # ✅ FIX: Added nosec comment to ignore hardcoded password warning in tests.
        User.objects.create_user(username='testuser', password='password123')  # nosec B106
    
    # Log the user in
    # ✅ FIX: Added nosec comment here as well for the same reason.
    client.login(username='testuser', password='password123')  # nosec B106
    
    return client
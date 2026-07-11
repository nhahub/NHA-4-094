import pytest
from app.core.config import settings

@pytest.fixture(scope="session", autouse=True)
def configure_test_settings():
    """Configure settings for the test runner session to ensure compatibility with legacy test user IDs."""
    settings.AUTH_MODE = "mock"
    settings.MOCK_USER_ID = "00000000-0000-0000-0000-000000000000"
    settings.APP_ENV = "development"
    settings.validate_auth_settings()

@pytest.fixture(autouse=True)
def mock_session_validation(request):
    """Automatically mock validate_session_ownership_and_document for legacy tests to maintain compatibility."""
    if "test_document_endpoints" in request.module.__name__:
        yield
        return

    from unittest.mock import AsyncMock, patch
    with patch("app.api.v1.ai.validate_session_ownership_and_document", new_callable=AsyncMock) as mock_val:
        mock_val.return_value = {}
        yield

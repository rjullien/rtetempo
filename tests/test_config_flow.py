"""Tests for config_flow.py module."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from custom_components.rtetempo.config_flow import ConfigFlow, OptionsFlowHandler
from custom_components.rtetempo.api_worker import BadRequest, ServerError, UnexpectedError
from custom_components.rtetempo.const import (
    DOMAIN,
    CONFIG_CLIENT_ID,
    CONFIG_CLIEND_SECRET,
    OPTION_ADJUSTED_DAYS,
)


# ============================================================================
# Tests for ConfigFlow (Requirements 11.1-11.6)
# ============================================================================

class TestConfigFlow:
    """Tests for ConfigFlow class."""

    @pytest.mark.asyncio
    async def test_async_step_user_no_input_shows_form(self):
        """Test that async_step_user shows form when no input provided."""
        flow = ConfigFlow()
        flow.hass = MagicMock()
        
        result = await flow.async_step_user(user_input=None)
        
        assert result["type"] == "form"
        assert result["step_id"] == "user"

    @pytest.mark.asyncio
    async def test_async_step_user_valid_credentials_creates_entry(self):
        """Test that valid credentials create an entry."""
        flow = ConfigFlow()
        flow.hass = MagicMock()
        flow.hass.async_add_executor_job = AsyncMock(return_value=None)
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock()
        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
        
        user_input = {
            CONFIG_CLIENT_ID: "valid_client_id",
            CONFIG_CLIEND_SECRET: "valid_client_secret",
        }
        
        with patch('custom_components.rtetempo.config_flow.application_tester'):
            result = await flow.async_step_user(user_input=user_input)
        
        flow.async_create_entry.assert_called_once()
        assert result["type"] == "create_entry"

    @pytest.mark.asyncio
    async def test_async_step_user_network_error(self):
        """Test that network error shows network_error."""
        from requests.exceptions import RequestException
        
        flow = ConfigFlow()
        flow.hass = MagicMock()
        flow.hass.async_add_executor_job = AsyncMock(side_effect=RequestException("Network error"))
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock()
        flow.async_show_form = MagicMock(return_value={"type": "form", "errors": {"base": "network_error"}})
        
        user_input = {
            CONFIG_CLIENT_ID: "client_id",
            CONFIG_CLIEND_SECRET: "client_secret",
        }
        
        result = await flow.async_step_user(user_input=user_input)
        
        assert result["errors"]["base"] == "network_error"

    @pytest.mark.asyncio
    async def test_async_step_user_oauth_error(self):
        """Test that OAuth error shows oauth_error."""
        from oauthlib.oauth2.rfc6749.errors import OAuth2Error
        
        flow = ConfigFlow()
        flow.hass = MagicMock()
        flow.hass.async_add_executor_job = AsyncMock(side_effect=OAuth2Error("OAuth error"))
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock()
        flow.async_show_form = MagicMock(return_value={"type": "form", "errors": {"base": "oauth_error"}})
        
        user_input = {
            CONFIG_CLIENT_ID: "client_id",
            CONFIG_CLIEND_SECRET: "client_secret",
        }
        
        result = await flow.async_step_user(user_input=user_input)
        
        assert result["errors"]["base"] == "oauth_error"

    @pytest.mark.asyncio
    async def test_async_step_user_bad_request_error(self):
        """Test that BadRequest error shows http_client_error."""
        flow = ConfigFlow()
        flow.hass = MagicMock()
        flow.hass.async_add_executor_job = AsyncMock(side_effect=BadRequest(400, "Bad request"))
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock()
        flow.async_show_form = MagicMock(return_value={"type": "form", "errors": {"base": "http_client_error"}})
        
        user_input = {
            CONFIG_CLIENT_ID: "client_id",
            CONFIG_CLIEND_SECRET: "client_secret",
        }
        
        result = await flow.async_step_user(user_input=user_input)
        
        assert result["errors"]["base"] == "http_client_error"

    @pytest.mark.asyncio
    async def test_async_step_user_server_error(self):
        """Test that ServerError shows http_server_error."""
        flow = ConfigFlow()
        flow.hass = MagicMock()
        flow.hass.async_add_executor_job = AsyncMock(side_effect=ServerError(500, "Server error"))
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock()
        flow.async_show_form = MagicMock(return_value={"type": "form", "errors": {"base": "http_server_error"}})
        
        user_input = {
            CONFIG_CLIENT_ID: "client_id",
            CONFIG_CLIEND_SECRET: "client_secret",
        }
        
        result = await flow.async_step_user(user_input=user_input)
        
        assert result["errors"]["base"] == "http_server_error"

    @pytest.mark.asyncio
    async def test_async_step_user_unexpected_error(self):
        """Test that UnexpectedError shows http_unexpected_error."""
        flow = ConfigFlow()
        flow.hass = MagicMock()
        flow.hass.async_add_executor_job = AsyncMock(side_effect=UnexpectedError(418, "Unexpected"))
        flow.async_set_unique_id = AsyncMock()
        flow._abort_if_unique_id_configured = MagicMock()
        flow.async_show_form = MagicMock(return_value={"type": "form", "errors": {"base": "http_unexpected_error"}})
        
        user_input = {
            CONFIG_CLIENT_ID: "client_id",
            CONFIG_CLIEND_SECRET: "client_secret",
        }
        
        result = await flow.async_step_user(user_input=user_input)
        
        assert result["errors"]["base"] == "http_unexpected_error"

    def test_async_get_options_flow(self):
        """Test that async_get_options_flow returns OptionsFlowHandler."""
        config_entry = MagicMock()
        result = ConfigFlow.async_get_options_flow(config_entry)
        assert isinstance(result, OptionsFlowHandler)


# ============================================================================
# Tests for OptionsFlowHandler (Requirements 12.1-12.2)
# ============================================================================

class TestOptionsFlowHandler:
    """Tests for OptionsFlowHandler class."""

    @pytest.mark.asyncio
    async def test_async_step_init_no_input_shows_form(self):
        """Test that async_step_init shows form when no input provided."""
        handler = OptionsFlowHandler()
        handler.config_entry = MagicMock()
        handler.config_entry.options = {OPTION_ADJUSTED_DAYS: False}
        handler.async_show_form = MagicMock(return_value={"type": "form", "step_id": "init"})
        
        result = await handler.async_step_init(user_input=None)
        
        assert result["type"] == "form"
        assert result["step_id"] == "init"

    @pytest.mark.asyncio
    async def test_async_step_init_with_input_creates_entry(self):
        """Test that async_step_init creates entry when input provided."""
        handler = OptionsFlowHandler()
        handler.config_entry = MagicMock()
        handler.config_entry.options = {OPTION_ADJUSTED_DAYS: False}
        handler.async_create_entry = MagicMock(return_value={"type": "create_entry"})
        
        user_input = {OPTION_ADJUSTED_DAYS: True}
        
        result = await handler.async_step_init(user_input=user_input)
        
        handler.async_create_entry.assert_called_once_with(title="", data=user_input)
        assert result["type"] == "create_entry"

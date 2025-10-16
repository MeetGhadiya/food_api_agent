"""
Test Suite for config.py - Configuration Management
Tests validation, defaults, and environment variable handling
"""

import pytest
import os
from unittest.mock import patch
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config


class TestConfigDefaults:
    """Test default configuration values"""
    
    def test_ollama_defaults(self):
        """Test Ollama default configuration"""
        assert Config.USE_OLLAMA == True
        assert Config.OLLAMA_MODEL == "llama3.2:3b"
        assert Config.OLLAMA_URL == "http://localhost:11434/api/chat"
        assert Config.OLLAMA_TIMEOUT == 90
        assert Config.OLLAMA_MAX_RETRIES == 3
    
    def test_redis_defaults(self):
        """Test Redis default configuration"""
        assert Config.REDIS_HOST == "localhost"
        assert Config.REDIS_PORT == 6379
        assert Config.REDIS_DB == 0
        assert Config.REDIS_TTL == 600
    
    def test_api_defaults(self):
        """Test Backend API default configuration"""
        assert Config.BACKEND_URL == "http://localhost:8000"
        assert Config.API_TIMEOUT == 10
        assert Config.API_MAX_RETRIES == 3
    
    def test_flask_defaults(self):
        """Test Flask default configuration"""
        assert Config.FLASK_PORT == 5000
        assert Config.FLASK_HOST == "0.0.0.0"
        assert Config.FLASK_DEBUG == False
    
    def test_logging_defaults(self):
        """Test logging default configuration"""
        assert Config.LOG_LEVEL == "INFO"
        assert Config.LOG_DIR == "logs"
        assert Config.LOG_FILE == "agent.log"


class TestConfigEnvironmentVariables:
    """Test environment variable override"""
    
    @patch.dict(os.environ, {"OLLAMA_MODEL": "llama3.2:1b"})
    def test_ollama_model_override(self):
        """Test OLLAMA_MODEL environment variable override"""
        # Need to reload config to pick up new env var
        from importlib import reload
        import config as config_module
        reload(config_module)
        assert config_module.Config.OLLAMA_MODEL == "llama3.2:1b"
    
    @patch.dict(os.environ, {"REDIS_PORT": "6380"})
    def test_redis_port_override(self):
        """Test REDIS_PORT environment variable override"""
        from importlib import reload
        import config as config_module
        reload(config_module)
        assert config_module.Config.REDIS_PORT == 6380
    
    @patch.dict(os.environ, {"API_TIMEOUT": "30"})
    def test_api_timeout_override(self):
        """Test API_TIMEOUT environment variable override"""
        from importlib import reload
        import config as config_module
        reload(config_module)
        assert config_module.Config.API_TIMEOUT == 30


class TestConfigValidation:
    """Test configuration validation logic"""
    
    def test_valid_config(self):
        """Test that default configuration passes validation"""
        is_valid, errors = Config.validate()
        assert is_valid == True
        assert len(errors) == 0
    
    @patch.dict(os.environ, {"USE_OLLAMA": "true", "OLLAMA_URL": ""})
    def test_missing_ollama_url(self):
        """Test validation fails when Ollama URL missing but USE_OLLAMA=True"""
        from importlib import reload
        import config as config_module
        reload(config_module)
        is_valid, errors = config_module.Config.validate()
        assert is_valid == False
        assert any("OLLAMA_URL" in error for error in errors)
    
    @patch.dict(os.environ, {"REDIS_PORT": "99999"})
    def test_invalid_redis_port(self):
        """Test validation fails with invalid Redis port"""
        from importlib import reload
        import config as config_module
        reload(config_module)
        is_valid, errors = config_module.Config.validate()
        assert is_valid == False
        assert any("REDIS_PORT" in error for error in errors)
    
    @patch.dict(os.environ, {"OLLAMA_TIMEOUT": "5"})
    def test_ollama_timeout_too_low(self):
        """Test validation fails when Ollama timeout too low"""
        from importlib import reload
        import config as config_module
        reload(config_module)
        is_valid, errors = config_module.Config.validate()
        assert is_valid == False
        assert any("OLLAMA_TIMEOUT" in error for error in errors)
    
    @patch.dict(os.environ, {"API_TIMEOUT": "0"})
    def test_api_timeout_zero(self):
        """Test validation fails with zero API timeout"""
        from importlib import reload
        import config as config_module
        reload(config_module)
        is_valid, errors = config_module.Config.validate()
        assert is_valid == False
        assert any("API_TIMEOUT" in error for error in errors)


class TestConfigPrinting:
    """Test configuration printing functionality"""
    
    def test_print_config_runs(self, capsys):
        """Test that print_config() executes without errors"""
        Config.print_config()
        captured = capsys.readouterr()
        assert "FOODIEEXPRESS AGENT CONFIGURATION" in captured.out
        assert "Ollama Configuration" in captured.out
        assert "Redis Configuration" in captured.out


class TestConfigTypes:
    """Test configuration value types"""
    
    def test_boolean_types(self):
        """Test boolean configuration values"""
        assert isinstance(Config.USE_OLLAMA, bool)
        assert isinstance(Config.FLASK_DEBUG, bool)
    
    def test_integer_types(self):
        """Test integer configuration values"""
        assert isinstance(Config.REDIS_PORT, int)
        assert isinstance(Config.REDIS_DB, int)
        assert isinstance(Config.REDIS_TTL, int)
        assert isinstance(Config.OLLAMA_TIMEOUT, int)
        assert isinstance(Config.API_TIMEOUT, int)
        assert isinstance(Config.FLASK_PORT, int)
    
    def test_string_types(self):
        """Test string configuration values"""
        assert isinstance(Config.OLLAMA_MODEL, str)
        assert isinstance(Config.OLLAMA_URL, str)
        assert isinstance(Config.REDIS_HOST, str)
        assert isinstance(Config.BACKEND_URL, str)
        assert isinstance(Config.FLASK_HOST, str)
        assert isinstance(Config.LOG_LEVEL, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

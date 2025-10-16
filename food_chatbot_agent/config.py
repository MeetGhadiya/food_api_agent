"""
FoodieExpress Agent - Configuration Management
==============================================
Centralized configuration with environment variable validation

This module handles all configuration settings for the AI chatbot agent,
including validation, defaults, and environment-specific settings.

Version: 4.0
Author: Meet Ghadiya
Date: October 2025
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Central configuration class for the FoodieExpress Agent.
    
    All environment variables are loaded here with appropriate defaults
    and validation to ensure the agent runs stably in any environment.
    """
    
    # ==================== AI MODEL CONFIGURATION ====================
    
    # CRITICAL: Force Ollama usage for stability (from test reports)
    USE_OLLAMA: bool = True  # Always use Ollama for stable, crash-free operation
    
    # Ollama Configuration
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
    OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "90"))  # 90 seconds max
    OLLAMA_MAX_RETRIES: int = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
    
    # Google Gemini Configuration (backup/fallback only)
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # ==================== BACKEND API CONFIGURATION ====================
    
    FASTAPI_BASE_URL: str = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
    BACKEND_TIMEOUT: int = int(os.getenv("BACKEND_TIMEOUT", "10"))  # 10 second timeout
    BACKEND_MAX_RETRIES: int = int(os.getenv("BACKEND_MAX_RETRIES", "3"))
    
    # ==================== REDIS CONFIGURATION ====================
    
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "true").lower() == "true"
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", "600"))  # 10 minutes default
    REDIS_CONNECTION_TIMEOUT: int = int(os.getenv("REDIS_CONNECTION_TIMEOUT", "5"))
    
    # ==================== FLASK SERVER CONFIGURATION ====================
    
    FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    FLASK_THREADS: int = int(os.getenv("FLASK_THREADS", "4"))
    
    # CORS Configuration
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:5174,http://localhost:3000,http://localhost:80"
    ).split(",")
    
    # ==================== SESSION MANAGEMENT ====================
    
    MAX_SESSION_MESSAGES: int = int(os.getenv("MAX_SESSION_MESSAGES", "20"))
    SESSION_CLEANUP_THRESHOLD: int = int(os.getenv("SESSION_CLEANUP_THRESHOLD", "100"))
    
    # ==================== LOGGING CONFIGURATION ====================
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")  # DEBUG, INFO, WARNING, ERROR
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/agent.log")
    LOG_MAX_SIZE: int = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # ==================== AGENT PERSONALITY ====================
    
    AGENT_NAME: str = os.getenv("AGENT_NAME", "Foodie")
    AGENT_VERSION: str = "4.0.0"
    USE_EMOJIS: bool = os.getenv("USE_EMOJIS", "true").lower() == "true"
    
    # ==================== FEATURE FLAGS ====================
    
    ENABLE_PERSONALIZATION: bool = os.getenv("ENABLE_PERSONALIZATION", "true").lower() == "true"
    ENABLE_PROACTIVE_REVIEWS: bool = os.getenv("ENABLE_PROACTIVE_REVIEWS", "true").lower() == "true"
    ENABLE_ADMIN_DASHBOARD: bool = os.getenv("ENABLE_ADMIN_DASHBOARD", "true").lower() == "true"
    
    # ==================== TESTING CONFIGURATION ====================
    
    TEST_MODE: bool = os.getenv("TEST_MODE", "false").lower() == "true"
    TEST_DELAY: float = float(os.getenv("TEST_DELAY", "0.5"))  # Delay between test requests
    
    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Validate the configuration and return any errors.
        
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check critical configurations
        if cls.USE_OLLAMA and not cls.OLLAMA_URL:
            errors.append("OLLAMA_URL is required when USE_OLLAMA is True")
        
        if not cls.USE_OLLAMA and not cls.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY is required when USE_OLLAMA is False")
        
        if not cls.FASTAPI_BASE_URL:
            errors.append("FASTAPI_BASE_URL is required")
        
        # Validate port ranges
        if not (1 <= cls.REDIS_PORT <= 65535):
            errors.append(f"REDIS_PORT must be between 1-65535, got {cls.REDIS_PORT}")
        
        if not (1 <= cls.FLASK_PORT <= 65535):
            errors.append(f"FLASK_PORT must be between 1-65535, got {cls.FLASK_PORT}")
        
        # Validate timeouts
        if cls.OLLAMA_TIMEOUT < 10:
            errors.append("OLLAMA_TIMEOUT should be at least 10 seconds")
        
        if cls.BACKEND_TIMEOUT < 5:
            errors.append("BACKEND_TIMEOUT should be at least 5 seconds")
        
        # Validate retry counts
        if cls.OLLAMA_MAX_RETRIES < 1:
            errors.append("OLLAMA_MAX_RETRIES must be at least 1")
        
        if cls.BACKEND_MAX_RETRIES < 1:
            errors.append("BACKEND_MAX_RETRIES must be at least 1")
        
        return (len(errors) == 0, errors)
    
    @classmethod
    def print_config(cls):
        """Print the current configuration (for debugging)"""
        print("=" * 80)
        print(f"🤖 {cls.AGENT_NAME} Agent v{cls.AGENT_VERSION} - Configuration")
        print("=" * 80)
        print("\n📊 AI Model Configuration:")
        print(f"  • AI Mode: {'LOCAL OLLAMA' if cls.USE_OLLAMA else 'GOOGLE GEMINI'}")
        if cls.USE_OLLAMA:
            print(f"  • Ollama Model: {cls.OLLAMA_MODEL}")
            print(f"  • Ollama URL: {cls.OLLAMA_URL}")
            print(f"  • Ollama Timeout: {cls.OLLAMA_TIMEOUT}s")
            print(f"  • Max Retries: {cls.OLLAMA_MAX_RETRIES}")
        else:
            print(f"  • Gemini Model: {cls.GEMINI_MODEL}")
            print(f"  • API Key: {'✓ Configured' if cls.GOOGLE_API_KEY else '✗ Missing'}")
        
        print("\n🔗 Backend Configuration:")
        print(f"  • FastAPI URL: {cls.FASTAPI_BASE_URL}")
        print(f"  • Timeout: {cls.BACKEND_TIMEOUT}s")
        print(f"  • Max Retries: {cls.BACKEND_MAX_RETRIES}")
        
        print("\n💾 Redis Configuration:")
        print(f"  • Enabled: {cls.REDIS_ENABLED}")
        if cls.REDIS_ENABLED:
            print(f"  • Host: {cls.REDIS_HOST}:{cls.REDIS_PORT}")
            print(f"  • Database: {cls.REDIS_DB}")
            print(f"  • TTL: {cls.REDIS_TTL}s")
            print(f"  • Password: {'✓ Set' if cls.REDIS_PASSWORD else '✗ None'}")
        
        print("\n🌐 Flask Server Configuration:")
        print(f"  • Host: {cls.FLASK_HOST}:{cls.FLASK_PORT}")
        print(f"  • Debug Mode: {cls.FLASK_DEBUG}")
        print(f"  • Threads: {cls.FLASK_THREADS}")
        print(f"  • CORS Origins: {', '.join(cls.CORS_ORIGINS[:3])}{'...' if len(cls.CORS_ORIGINS) > 3 else ''}")
        
        print("\n📝 Logging Configuration:")
        print(f"  • Level: {cls.LOG_LEVEL}")
        print(f"  • File: {cls.LOG_FILE}")
        print(f"  • Max Size: {cls.LOG_MAX_SIZE // 1024 // 1024}MB")
        print(f"  • Backup Count: {cls.LOG_BACKUP_COUNT}")
        
        print("\n✨ Feature Flags:")
        print(f"  • Personalization: {cls.ENABLE_PERSONALIZATION}")
        print(f"  • Proactive Reviews: {cls.ENABLE_PROACTIVE_REVIEWS}")
        print(f"  • Admin Dashboard: {cls.ENABLE_ADMIN_DASHBOARD}")
        print(f"  • Use Emojis: {cls.USE_EMOJIS}")
        
        print("\n🧪 Testing Configuration:")
        print(f"  • Test Mode: {cls.TEST_MODE}")
        if cls.TEST_MODE:
            print(f"  • Test Delay: {cls.TEST_DELAY}s")
        
        print("=" * 80)
        
        # Validate and show any errors
        is_valid, validation_errors = cls.validate()
        if not is_valid:
            print("\n⚠️  CONFIGURATION ERRORS:")
            for error in validation_errors:
                print(f"  ✗ {error}")
            print("=" * 80)
            return False
        else:
            print("\n✅ Configuration validated successfully!")
            print("=" * 80)
            return True


# Create a singleton instance
config = Config()


# Validation function for easy import
def validate_config() -> bool:
    """
    Validate the configuration and print results.
    
    Returns:
        bool: True if valid, False otherwise
    """
    return config.print_config()


if __name__ == "__main__":
    # When run directly, print and validate configuration
    validate_config()

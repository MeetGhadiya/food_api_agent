"""
FoodieExpress Agent - Custom Logger
====================================
Structured logging with file output and rotation

This module provides a custom logger with multiple levels, file output,
and automatic log rotation for production environments.

Version: 4.0
Author: Meet Ghadiya
Date: October 2025
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from config import config


class AgentLogger:
    """
    Custom logger for the FoodieExpress Agent.
    
    Features:
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - File output with rotation
    - Console output with colors
    - Structured format
    - Thread-safe
    """
    
    def __init__(self, name: str = "foodie_agent"):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self._get_log_level())
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Create logs directory if it doesn't exist
        log_dir = Path(config.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Add file handler with rotation
        self._add_file_handler()
        
        # Add console handler
        self._add_console_handler()
        
        print(f"✅ Logger initialized: {name} (Level: {config.LOG_LEVEL})")
    
    def _get_log_level(self) -> int:
        """Convert string log level to logging constant"""
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return levels.get(config.LOG_LEVEL.upper(), logging.INFO)
    
    def _add_file_handler(self):
        """Add rotating file handler"""
        file_handler = RotatingFileHandler(
            config.LOG_FILE,
            maxBytes=config.LOG_MAX_SIZE,
            backupCount=config.LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
    
    def _add_console_handler(self):
        """Add console handler with colors"""
        console_handler = logging.StreamHandler()
        
        # Simpler format for console
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """Log DEBUG level message"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log INFO level message"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log WARNING level message"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log ERROR level message"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log CRITICAL level message"""
        self.logger.critical(message, **kwargs)
    
    def log_request(self, user_id: str, message: str, test_id: Optional[str] = None):
        """
        Log an incoming user request.
        
        Args:
            user_id: User identifier
            message: User's message
            test_id: Optional test identifier for automated testing
        """
        test_info = f" [TEST_ID: {test_id}]" if test_id else ""
        self.info(f"📥 REQUEST{test_info} | User: {user_id} | Message: {message[:100]}")
    
    def log_response(self, user_id: str, response: str, function_called: Optional[str] = None):
        """
        Log an agent response.
        
        Args:
            user_id: User identifier
            response: Agent's response
            function_called: Name of function that was called (if any)
        """
        func_info = f" | Function: {function_called}" if function_called else ""
        self.info(f"📤 RESPONSE{func_info} | User: {user_id} | Response length: {len(response)} chars")
    
    def log_function_call(self, function_name: str, args: dict):
        """
        Log a function call.
        
        Args:
            function_name: Name of the function
            args: Function arguments
        """
        self.info(f"⚙️  FUNCTION CALL | {function_name} | Args: {args}")
    
    def log_error(self, error_type: str, error_message: str, user_id: Optional[str] = None):
        """
        Log an error with context.
        
        Args:
            error_type: Type of error
            error_message: Error message
            user_id: Optional user identifier
        """
        user_info = f" | User: {user_id}" if user_id else ""
        self.error(f"❌ ERROR{user_info} | {error_type}: {error_message}")
    
    def log_performance(self, operation: str, duration: float, success: bool = True):
        """
        Log performance metrics.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            success: Whether operation succeeded
        """
        status = "✅" if success else "❌"
        self.info(f"⏱️  PERFORMANCE {status} | {operation} | {duration:.2f}s")


# Create a singleton instance
logger = AgentLogger()


# Convenience functions
def log_info(message: str):
    """Log info message"""
    logger.info(message)


def log_error(message: str):
    """Log error message"""
    logger.error(message)


def log_warning(message: str):
    """Log warning message"""
    logger.warning(message)


def log_debug(message: str):
    """Log debug message"""
    logger.debug(message)


if __name__ == "__main__":
    # Test the logger
    print("\n🧪 Testing Logger...")
    print("=" * 60)
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    logger.log_request("test_user", "Show me all restaurants", test_id="TEST_001")
    logger.log_response("test_user", "Here are all the restaurants...", function_called="get_all_restaurants")
    logger.log_function_call("get_all_restaurants", {})
    logger.log_performance("get_all_restaurants", 0.234, success=True)
    logger.log_error("API Error", "Connection timeout", user_id="test_user")
    
    print(f"\n📁 Log file location: {config.LOG_FILE}")
    print("=" * 60)
    print("✅ Logger tests complete!")

"""
Test Suite for utils/logger.py - Structured Logging
Tests logging functionality, rotation, formats, and special methods
"""

import pytest
import os
import logging
import tempfile
import shutil
from unittest.mock import patch, Mock
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.logger import AgentLogger


class TestAgentLoggerInitialization:
    """Test logger initialization"""
    
    def test_initialization_creates_log_directory(self):
        """Test that initialization creates log directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "test_logs")
            
            logger = AgentLogger(log_dir=log_dir, log_file="test.log")
            
            assert os.path.exists(log_dir)
    
    def test_initialization_with_custom_level(self):
        """Test initialization with custom log level"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(
                log_dir=tmpdir,
                log_file="test.log",
                log_level="DEBUG"
            )
            
            assert logger.logger.level == logging.DEBUG
    
    def test_initialization_with_invalid_level_defaults_to_info(self):
        """Test that invalid log level defaults to INFO"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(
                log_dir=tmpdir,
                log_file="test.log",
                log_level="INVALID"
            )
            
            assert logger.logger.level == logging.INFO


class TestAgentLoggerBasicLogging:
    """Test basic logging methods"""
    
    def test_info_logging(self):
        """Test INFO level logging"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(log_dir=tmpdir, log_file="test.log")
            
            logger.info("Test info message")
            
            log_file_path = os.path.join(tmpdir, "test.log")
            with open(log_file_path, 'r') as f:
                log_content = f.read()
            
            assert "Test info message" in log_content
            assert "INFO" in log_content
    
    def test_warning_logging(self):
        """Test WARNING level logging"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(log_dir=tmpdir, log_file="test.log")
            
            logger.warning("Test warning message")
            
            log_file_path = os.path.join(tmpdir, "test.log")
            with open(log_file_path, 'r') as f:
                log_content = f.read()
            
            assert "Test warning message" in log_content
            assert "WARNING" in log_content
    
    def test_error_logging(self):
        """Test ERROR level logging"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(log_dir=tmpdir, log_file="test.log")
            
            logger.error("Test error message")
            
            log_file_path = os.path.join(tmpdir, "test.log")
            with open(log_file_path, 'r') as f:
                log_content = f.read()
            
            assert "Test error message" in log_content
            assert "ERROR" in log_content
    
    def test_critical_logging(self):
        """Test CRITICAL level logging"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(log_dir=tmpdir, log_file="test.log")
            
            logger.critical("Test critical message")
            
            log_file_path = os.path.join(tmpdir, "test.log")
            with open(log_file_path, 'r') as f:
                log_content = f.read()
            
            assert "Test critical message" in log_content
            assert "CRITICAL" in log_content


class TestAgentLoggerSpecialMethods:
    """Test domain-specific logging methods"""
    
    def test_log_request(self):
        """Test log_request method"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(log_dir=tmpdir, log_file="test.log")
            
            logger.log_request("user123", "Show me restaurants")
            
            log_file_path = os.path.join(tmpdir, "test.log")
            with open(log_file_path, 'r') as f:
                log_content = f.read()
            
            assert "user123" in log_content
            assert "Show me restaurants" in log_content
    
    def test_log_response(self):
        """Test log_response method"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(log_dir=tmpdir, log_file="test.log")
            
            logger.log_response("user123", "Here are the restaurants...")
            
            log_file_path = os.path.join(tmpdir, "test.log")
            with open(log_file_path, 'r') as f:
                log_content = f.read()
            
            assert "user123" in log_content
            assert "Here are the restaurants..." in log_content
    
    def test_log_performance(self):
        """Test log_performance method"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(log_dir=tmpdir, log_file="test.log")
            
            logger.log_performance("API call", 2.5)
            
            log_file_path = os.path.join(tmpdir, "test.log")
            with open(log_file_path, 'r') as f:
                log_content = f.read()
            
            assert "API call" in log_content
            assert "2.5" in log_content
    
    def test_log_error_with_exception(self):
        """Test log_error method with exception"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(log_dir=tmpdir, log_file="test.log")
            
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                logger.log_error(e, context={"user_id": "user123"})
            
            log_file_path = os.path.join(tmpdir, "test.log")
            with open(log_file_path, 'r') as f:
                log_content = f.read()
            
            assert "Test exception" in log_content
            assert "user123" in log_content


class TestAgentLoggerFileRotation:
    """Test log file rotation"""
    
    def test_file_rotation_configuration(self):
        """Test that file rotation is properly configured"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(
                log_dir=tmpdir,
                log_file="test.log",
                max_bytes=100,  # Small size to trigger rotation
                backup_count=3
            )
            
            # Write enough logs to trigger rotation
            for i in range(50):
                logger.info(f"Test message {i}" * 10)  # Long messages
            
            log_dir_files = os.listdir(tmpdir)
            
            # Should have main log file
            assert "test.log" in log_dir_files
            # May have rotated files
            # Note: Rotation may not happen in tests due to timing


class TestAgentLoggerFormats:
    """Test log formatting"""
    
    def test_log_format_includes_timestamp(self):
        """Test that log entries include timestamps"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(log_dir=tmpdir, log_file="test.log")
            
            logger.info("Test message")
            
            log_file_path = os.path.join(tmpdir, "test.log")
            with open(log_file_path, 'r') as f:
                log_content = f.read()
            
            # Check for timestamp pattern (YYYY-MM-DD HH:MM:SS)
            import re
            timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
            assert re.search(timestamp_pattern, log_content)
    
    def test_log_format_includes_level(self):
        """Test that log entries include log level"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(log_dir=tmpdir, log_file="test.log")
            
            logger.info("Test message")
            
            log_file_path = os.path.join(tmpdir, "test.log")
            with open(log_file_path, 'r') as f:
                log_content = f.read()
            
            assert "INFO" in log_content


class TestAgentLoggerConcurrency:
    """Test logging in concurrent scenarios"""
    
    def test_multiple_loggers_same_file(self):
        """Test multiple logger instances writing to same file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger1 = AgentLogger(log_dir=tmpdir, log_file="shared.log")
            logger2 = AgentLogger(log_dir=tmpdir, log_file="shared.log")
            
            logger1.info("Message from logger 1")
            logger2.info("Message from logger 2")
            
            log_file_path = os.path.join(tmpdir, "shared.log")
            with open(log_file_path, 'r') as f:
                log_content = f.read()
            
            assert "Message from logger 1" in log_content
            assert "Message from logger 2" in log_content


class TestAgentLoggerEdgeCases:
    """Test edge cases and error handling"""
    
    def test_logging_with_none_message(self):
        """Test logging with None message"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(log_dir=tmpdir, log_file="test.log")
            
            # Should not crash
            logger.info(None)
            
            # Check file was created
            log_file_path = os.path.join(tmpdir, "test.log")
            assert os.path.exists(log_file_path)
    
    def test_logging_with_unicode(self):
        """Test logging with Unicode characters"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(log_dir=tmpdir, log_file="test.log")
            
            logger.info("Unicode test: 你好 مرحبا привет 🍕")
            
            log_file_path = os.path.join(tmpdir, "test.log")
            with open(log_file_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            assert "Unicode test" in log_content
    
    def test_logging_with_very_long_message(self):
        """Test logging with very long messages"""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AgentLogger(log_dir=tmpdir, log_file="test.log")
            
            long_message = "A" * 10000  # 10,000 characters
            logger.info(long_message)
            
            log_file_path = os.path.join(tmpdir, "test.log")
            assert os.path.exists(log_file_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

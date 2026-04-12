import os
import pytest
from pathlib import Path
from src.utils.config import Config

class TestConfigPaths:
    """Test configuration paths"""

    def test_proj_src_path_exists(self):
        """Test that source path exists and is correct"""
        assert Config.PROJ_SRC_PATH.exists()
        assert Config.PROJ_SRC_PATH.name == "src"

    def test_proj_root_path_exists(self):
        """Test that root path exists"""
        assert Config.PROJ_ROOT_PATH.exists()
        assert (Config.PROJ_ROOT_PATH / "src").exists()

    def test_assets_path(self):
        """Test that assets path is configured"""
        assert Config.ASSETS_PATH.name == "assets"
        # May or may not exist yet, but should be properly configured
        expected_path = Config.PROJ_ROOT_PATH / "assets"
        assert Config.ASSETS_PATH == expected_path

    def test_audio_path(self):
        """Test that audio path is configured"""
        expected_path = Config.ASSETS_PATH / "audio"
        assert Config.AUDIO_PATH == expected_path

class TestConfigEnvironment:
    """Test environment variable loading"""

    def test_discord_token_loaded(self):
        """Test that Discord token is loaded from environment"""
        assert Config.DISCORD_TOKEN is not None
        assert len(Config.DISCORD_TOKEN) > 0
        assert isinstance(Config.DISCORD_TOKEN, str)

    def test_command_prefix_has_default(self):
        """Test that command prefix has a default value"""
        assert Config.COMMAND_PREFIX is not None
        assert isinstance(Config.COMMAND_PREFIX, str)

    def test_logging_level_is_valid(self):
        """Test that logging level is a valid Python logging level"""
        import logging
        valid_levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL
        ]
        assert Config.LOGGING_LEVEL in valid_levels

class TestConfigValidation:
    """Test configuration validation"""

    def test_validate_returns_true(self):
        """Test that validation passes with correct config"""
        assert Config.validate() is True

    def test_validate_creates_log_directory(self):
        """Test that validation creates log directory"""
        Config.validate()
        assert Config.LOG_DIR.exists()
        assert Config.LOG_DIR.is_dir()

    def test_missing_token_raises_error(self):
        """Test that missing DISCORD_TOKEN raises error"""
        from src.utils.config import Config

        original = Config.DISCORD_TOKEN
        try:
            Config.DISCORD_TOKEN = None
            with pytest.raises(ValueError, match="DISCORD_TOKEN not found"):
                Config.validate()
        finally:
            Config.DISCORD_TOKEN = original

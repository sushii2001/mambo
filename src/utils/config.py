import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables once
load_dotenv()

class Config:
    """Centralized configuration management"""

    # Paths
    PROJ_SRC_PATH = Path(__file__).parent.parent  # Points to src/
    PROJ_ROOT_PATH = PROJ_SRC_PATH.parent  # Points to mambo/
    ASSETS_PATH = PROJ_ROOT_PATH / "assets"
    AUDIO_PATH = ASSETS_PATH / "audio"

    # Discord
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")

    # Logging
    LOG_DIR = PROJ_ROOT_PATH / "logs"
    DISCORD_LOG_PATH = LOG_DIR / "discord.log"
    LOGGING_LEVEL = getattr(logging, os.getenv("LOGGING_LEVEL", "INFO"))

    # Big clock feature timing
    # HOUR_INTERVAL controls scheduler cadence.
    # BIG_CLOCK_PERIOD controls max playback time per trigger.
    HOUR_INTERVAL = 60
    BIG_CLOCK_PERIOD = 9

    @classmethod
    def validate(cls):
        """Validate required config exists"""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN not found in environment variables")

        # Create necessary directories
        cls.LOG_DIR.mkdir(exist_ok=True)

        return True

# Validate on import
Config.validate()
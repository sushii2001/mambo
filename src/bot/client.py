import discord
from discord.ext import commands
import logging
from src.utils.config import Config
from .tasks import start_bigclock_scheduler

class MamboBot(commands.Bot):
    """
    Custom Discord bot client

    Build flow:
        - setup_hook
        - load_commands
        - on_ready
    """
    def __init__(self, command_prefix="!"):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        intents.voice_states = True
        self.logger = self._setup_logger()

        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents
        )

    def _setup_logger(self):
        """Setup bot-specific logger"""
        logger = logging.getLogger("discord_logger")
        logger.setLevel(Config.LOGGING_LEVEL)
        logger.propagate = False

        # Remove any existing handlers to avoid duplicates
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler
        file_handler = logging.FileHandler(
            filename=Config.DISCORD_LOG_PATH,
            encoding="utf-8",
            mode="w"
        )
        file_handler.setLevel(Config.LOGGING_LEVEL)
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(Config.LOGGING_LEVEL)
        console_handler.setFormatter(formatter)

        # Add both handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    async def setup_hook(self):
        """Called when the bot is starting up"""
        self.logger.info("Command tree sync start")
        # Load commands/cogs here
        await self.load_commands()

        # Sync slash commands
        await self.tree.sync()

        # Start periodic big clock scheduler (idempotent helper).
        start_bigclock_scheduler(self)
        self.logger.info("Command tree sync done")

    async def load_commands(self):
        """Load all command modules"""
        extensions = [
            'src.bot.commands',
            # 'bot.handlers', # No longer needed
            # Add more as needed
        ]

        for extension in extensions:
            try:
                self.logger.info(f"Loading extension: {extension}")
                await self.load_extension(extension)
                self.logger.info(f"Successfully loaded {extension}")
            except Exception as e:
                self.logger.error(f"Failed to load {extension}: {e}", exc_info=True)
                raise

    async def on_ready(self):
        """Called when bot is ready"""
        self.logger.info(f'{self.user} has connected to Discord!')
        self.logger.info(f'Bot is in {len(self.guilds)} guilds')
        for guild in self.guilds:
            self.logger.info(f'Guild: {guild.name} (ID: {guild.id})')
        self.logger.info(f'Bot intents: guilds={self.intents.guilds}, members={self.intents.members}, voice_states={self.intents.voice_states}, message_content={self.intents.message_content}')

    def run_bot(self):
        """Start the bot with error handling"""
        try:
            self.logger.info("Starting bot...")
            self.run(
                Config.DISCORD_TOKEN,
                log_handler=None,
                log_level=Config.LOGGING_LEVEL
            )
        except KeyboardInterrupt:
            self.logger.info("Bot stopped manually (Ctrl+C)")
        except discord.LoginFailure:
            self.logger.critical("Invalid Discord token! Check your .env file")
        except discord.HTTPException as e:
            self.logger.error(f"HTTP error occurred: {e}", exc_info=True)
        except Exception as e:
            self.logger.critical(f"Unexpected error occurred: {e}", exc_info=True)
        finally:
            self.logger.info("Bot shutdown complete")

def main():
    print("This is bot client")

if __name__ == "__main__":
    main()
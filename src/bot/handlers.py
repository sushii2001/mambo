from discord.ext import commands
import logging

logger = logging.getLogger("discord_logger")

class EventHandlers(commands.Cog):
    """Event handlers for the bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle incoming messages"""
        if message.author.bot:
            return

        # Your message handling logic here
        logger.debug(f"Message from {message.author}: {message.content}")

        # Process commands
        await self.bot.process_commands(message)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle new members"""
        logger.info(f"{member} joined the server")

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        """Handle errors"""
        logger.error(f"Error in {event}", exc_info=True)

async def setup(bot):
    """Load the cog"""
    await bot.add_cog(EventHandlers(bot))
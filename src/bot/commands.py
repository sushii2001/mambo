from discord.ext import commands
from discord import app_commands
import discord
import logging
import uuid

from .voice import get_interaction_voice_channel, int_disconnect_voice
from .tasks import BIG_CLOCK_LIST_EN, BIG_CLOCK_RING_PATH, BIG_CLOCK_PERIOD

logger = logging.getLogger("discord_logger")

class BasicCommands(commands.Cog):
    """Basic bot commands"""

    def __init__(self, bot):
        self.bot = bot

    # ---------- Commands ----------
    # prefix commands
    @commands.command(name="ping")
    async def ping(self, ctx):
        """Check bot latency"""
        latency_time = round(self.bot.latency * 1000)
        marker = uuid.uuid4()
        latency_msg = f"Pong! Latency: {latency_time}ms"
        logger.debug(f"{latency_msg}, {marker}")
        await ctx.send(latency_msg)

    # ---------- Interactions ----------
    # slash commands
    @app_commands.command(name="hello", description="Say hello!")
    async def hello(self, interaction: discord.Interaction):
        """Slash command example"""
        await interaction.response.send_message(f"Hello {interaction.user.mention}!")

    @app_commands.command(name="join", description="Command bot to join voice channel")
    async def join(self, interaction: discord.Interaction):
        ch = get_interaction_voice_channel(interaction)
        if not ch:
            await interaction.response.send_message(
                "❌ You must be in a voice channel.", ephemeral=True
            )
            return

        vc = interaction.guild.voice_client if interaction.guild else None

        try:
            if vc and vc.is_connected():
                if vc.channel != ch:
                    await vc.move_to(ch)
            else:
                await ch.connect()

            await interaction.response.send_message("✅ Joined voice channel.")

        except Exception:
            logger.exception("Voice join failed")
            await interaction.response.send_message(
                "❌ Failed to join voice channel.", ephemeral=True
            )

    @app_commands.command(name="leave", description="Command bot to leave voice channel")
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client if interaction.guild else None

        try:
            success = await int_disconnect_voice(vc)

            if success:
                await interaction.response.send_message("✅ Disconnected.")
            else:
                await interaction.response.send_message(
                    "❌ Not connected to a voice channel.", ephemeral=True
                )
        except Exception:
            logger.exception("Voice disconnect failed")
            await interaction.response.send_message(
                "❌ Failed to leave voice channel.", ephemeral=True
            )

    @app_commands.command(name="setbigclock", description="Set big clock")
    async def setbigclock(self, interaction: discord.Interaction, enable: bool):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.", ephemeral=True
            )
            return

        ch = get_interaction_voice_channel(interaction)
        if not ch:
            await interaction.response.send_message(
                "❌ You must be in a voice channel.", ephemeral=True
            )
            return

        try:
            BIG_CLOCK_LIST_EN[guild.id] = {
                "channel_id": ch.id,
                "audio": BIG_CLOCK_RING_PATH,
                "audio_path": BIG_CLOCK_RING_PATH,
                "seconds": BIG_CLOCK_PERIOD,
                "enable": enable,
            }

            await interaction.response.send_message(
                f"✅ Set Big Clock is {enable} from {interaction.user.mention}!"
            )
        except Exception:
            logger.exception("Failed to set big clock configuration")
            await interaction.response.send_message(
                "❌ Failed to set big clock.", ephemeral=True
            )

async def setup(bot):
    """Load the cog"""
    await bot.add_cog(BasicCommands(bot))
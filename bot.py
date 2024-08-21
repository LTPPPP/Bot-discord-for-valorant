# bot.py
import discord
from discord.ext import commands
import logging

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

logging.basicConfig(level=logging.DEBUG)

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)
        self.muted_channels = set()

    async def setup_hook(self):
        logging.debug("Starting command sync...")
        try:
            synced = await self.tree.sync(guild=None)  # Sync globally or to a specific guild.
            logging.info(f"Synced {len(synced)} command(s)")
        except discord.HTTPException as e:
            logging.error(f"HTTPException during sync: {e}")
        except discord.Forbidden as e:
            logging.error(f"Forbidden error during sync: {e}")
        except Exception as e:
            logging.error(f"Unknown error during sync: {e}")

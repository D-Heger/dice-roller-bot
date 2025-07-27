import discord
from discord.ext import commands
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.config import Config

# Set up logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class DnDBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        # Only enable message_content if needed for prefix commands
        # This is a privileged intent that needs to be enabled in Discord Developer Portal
        intents.message_content = True
        
        super().__init__(
            command_prefix=Config.PREFIX,
            intents=intents,
            help_command=None  # We'll use our custom help
        )
    
    async def setup_hook(self):
        """Load cogs"""
        cogs = ['bot.cog.dice_rolling', 'bot.cog.help']
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")
    
    async def on_ready(self):
        """Bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        await self.change_presence(
            activity=discord.Game(name=f"D&D | {Config.PREFIX}help")
        )
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore command not found
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
            return
        
        if isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument provided.")
            return
        
        # Log unexpected errors
        logger.error(f"Unexpected error: {error}", exc_info=True)
        await ctx.send("❌ An unexpected error occurred.")

def create_bot():
    """Create and return bot instance"""
    Config.validate()
    return DnDBot()
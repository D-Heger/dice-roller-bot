import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Bot Configuration
    TOKEN = os.getenv('DISCORD_TOKEN')
    PREFIX = os.getenv('BOT_PREFIX', '!')
    
    # Dice Configuration
    MAX_DICE = int(os.getenv('MAX_DICE', 100))
    MAX_SIDES = int(os.getenv('MAX_SIDES', 1000))
    MAX_MULTIROLL = int(os.getenv('MAX_MULTIROLL', 10))
    
    # Animation Configuration
    ENABLE_ANIMATIONS = os.getenv('ENABLE_ANIMATIONS', 'true').lower() == 'true'
    ANIMATION_DELAY = float(os.getenv('ANIMATION_DELAY', 0.2))
    
    # Development Configuration
    ENABLE_DEV_COMMANDS = os.getenv('ENABLE_DEV_COMMANDS', 'false').lower() == 'true'
    ENABLE_HOT_RELOAD = os.getenv('ENABLE_HOT_RELOAD', 'false').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.TOKEN:
            raise ValueError("DISCORD_TOKEN is required. Please set it in your .env file")
        return True
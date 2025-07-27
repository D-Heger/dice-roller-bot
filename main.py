#!/usr/bin/env python3
"""
D&D Dice Bot - A Discord bot for rolling dice in D&D games
"""

import asyncio
import logging
from bot.bot import create_bot
from config.config import Config

logger = logging.getLogger(__name__)

async def main():
    """Main entry point"""
    try:
        bot = create_bot()
        await bot.start(Config.TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
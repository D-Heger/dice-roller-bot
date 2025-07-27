# D&D Dice Bot 🎲

A feature-rich Discord bot for rolling dice in Dungeons & Dragons 5th Edition games.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Discord.py Version](https://img.shields.io/badge/discord.py-2.3.0%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features ✨

- **Flexible Dice Rolling**: Support for complex dice expressions (e.g., `2d20+1d6+5`)
- **D&D Specific Rolls**: Advantage, disadvantage, and ability score generation
- **Multi-rolling**: Roll the same expression multiple times
- **Critical Detection**: Automatic detection of natural 20s and 1s
- **Beautiful Embeds**: Clean, colored embed messages for all rolls
- **Error Handling**: Graceful error messages for invalid inputs

## Commands 📝

| Command | Description | Example |
|---------|-------------|---------|
| `!roll [expression]` | Roll dice with modifiers | `!roll 1d20+5` |
| `!advantage [modifier]` | Roll with advantage | `!adv +3` |
| `!disadvantage [modifier]` | Roll with disadvantage | `!dis +2` |
| `!stats` | Roll ability scores (4d6 drop lowest) | `!stats` |
| `!multiroll [times] [expr]` | Roll multiple times | `!m 6 4d6` |
| `!help [command]` | Show help information | `!help roll` |

### Command Aliases

- `!roll` → `!r`
- `!advantage` → `!adv`
- `!disadvantage` → `!dis`
- `!multiroll` → `!m`
- `!help` → `!h`

## Installation 🚀

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token ([Create one here](https://discord.com/developers/applications))

### Setup Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/dnd-dice-bot.git
   cd dnd-dice-bot
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**

    - Copy .env.example to .env

    ```bash
    cp .env.example .env
    ```

    - Add your Discord bot token to the `.env` file:

    ```plaintext
    DISCORD_TOKEN=your_bot_token_here <- Replace with your actual token
    ```

4. **Run the bot**

    ```bash
    python bot.py
    ```

## Configuration ⚙️

All configuration is done through environment variables in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| DISCORD_TOKEN | Your bot's Discord token | Required |
| BOT_PREFIX | Command prefix for the bot | `!` |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| MAX_DICE | Maximum number of dice per roll | `100` |
| MAX_SIDES | Maximum sides per die | `1000` |
| MAX_MULTIROLL | Maximum times for multiroll | `10` |

## Development 🛠️

### Project Structure

```plaintext
dice-roller-bot/
├── bot/                 # Bot core functionality
│   ├── cogs/           # Command groups
│   └── utils/          # Utility functions
├── config/             # Configuration management
└── main.py            # Entry point
```

### Adding New Commands

1. Create a new cog in the `bot/cogs/` directory.
2. Implement your commands using `@commands.command()`
3. Add the cog to the bot in `main.py`:

   ```python
   async def setup_hook(self):
        """Load cogs"""
        cogs = ['bot.cog.dice_rolling', 'bot.cog.help', 'your.cog.name'] <- Add your cog here
   ```

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

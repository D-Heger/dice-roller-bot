# D&D Dice Bot 🎲

A feature-rich Discord bot for rolling dice in Dungeons & Dragons 5th Edition games.

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Discord.py Version](https://img.shields.io/badge/discord.py-2.3.0%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features ✨

### Core Dice Rolling

 - **Flexible Dice Rolling**: Support for complex dice expressions (e.g., `2d20+1d6+5`)
 - **D&D Specific Rolls**: Advantage, disadvantage, and ability score generation
 - **Multi-rolling**: Roll the same expression multiple times
 - **Critical Detection**: Automatic detection of natural 20s and 1s on d20 rolls
 - **Animated Rolls**: Visual dice rolling animations with color cycling
 - **Beautiful Embeds**: Clean, colored embed messages for all rolls
 - **Error Handling**: Graceful error messages for invalid inputs
 - **Character Management**: Multi-user character system with JSON persistence, rich backstories, notes, and support for multiple stat systems (D&D 5e, Pathfinder, SPECIAL, Cortex, and more)

### Developer Features 🔧

- **Hot Reload**: Live code reloading during development without bot restart
- **File Watcher**: Automatic detection of code changes with auto-reload
- **Cog Management**: Load, unload, and reload individual bot components
- **Debug Commands**: Status monitoring and development utilities
- **Configurable**: Enable/disable dev features via environment variables

## Commands 📝

### Dice Rolling Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!roll [expression]` | Roll dice with modifiers | `!roll 1d20+5` |
| `!advantage [modifier]` | Roll with advantage | `!adv +3` |
| `!disadvantage [modifier]` | Roll with disadvantage | `!dis +2` |
| `!stats [system]` | Roll ability scores with different systems | `!stats pathfinder` |
| `!multiroll [times] [expr]` | Roll multiple times | `!m 6 4d6` |
| `!help [command]` | Show help information | `!help roll` |
| `!examples` | Show usage examples for commands | `!examples` |

### Character Management Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!char [name]` | View character or list all characters | `!char Gandalf` |
| `!char create <name> [role]` | Create a new character | `!char create "Gandalf" Wizard` |
| `!char list [user]` | List characters for user | `!char list @user` |
| `!char delete <name>` | Delete a character | `!char delete Gandalf` |
| `!char modify <subcommand>` | Modify character properties | See below |
| `!char backstory <name> [story]` | Set/view character backstory | `!char backstory Gandalf "A wise wizard..."` |
| `!char note <name> <text>` | Add a note to character | `!char note Gandalf "Learned new spell"` |
| `!char notes <name> [page]` | View character notes | `!char notes Gandalf 2` |

#### Character Modification Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!char modify name <old> <new>` | Change character name | `!char modify name Gandalf "Gandalf the Grey"` |
| `!char modify nickname <name> <nick>` | Set character nickname | `!char modify nickname Gandalf "Grey"` |
| `!char modify role <name> <role>` | Change character role | `!char modify role Gandalf "Wizard of the White Council"` |
| `!char modify system <name> <system> [yes/no]` | Change stat system | `!char modify system Gandalf pathfinder yes` |

### Developer Commands (when `ENABLE_DEV_COMMANDS=true`)

| Command | Description | Example |
|---------|-------------|---------|
| `!reload [cog]` | Reload specific cog or all cogs | `!reload dice_rolling` |
| `!load [cog]` | Load a new cog | `!load dice_rolling` |
| `!unload [cog]` | Unload a cog | `!unload dice_rolling` |
| `!listcogs` | List all loaded cogs | `!listcogs` |
| `!sync` | Sync slash commands | `!sync` |
| `!hotreload [on/off]` | Toggle automatic code reloading | `!hotreload on` |
| `!watchstatus` | Show file watcher debug info | `!watchstatus` |

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

### Basic Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| DISCORD_TOKEN | Your bot's Discord token | **Required** |
| BOT_PREFIX | Command prefix for the bot | `!` |
| LOG_LEVEL | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |

### Dice Rolling Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| MAX_DICE | Maximum number of dice per roll | `100` |
| MAX_SIDES | Maximum sides per die | `1000` |
| MAX_MULTIROLL | Maximum times for multiroll | `10` |

### Animation Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| ENABLE_ANIMATIONS | Enable dice rolling animations | `true` |
| ANIMATION_DELAY | Delay between animation frames (seconds) | `0.2` |

### Development Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| ENABLE_DEV_COMMANDS | Enable developer commands | `false` |
| ENABLE_HOT_RELOAD | Enable automatic file watching and reloading | `false` |

### Example `.env` file

```plaintext
# Required
DISCORD_TOKEN=your_bot_token_here

# Optional customization
BOT_PREFIX=!
LOG_LEVEL=INFO

# Dice limits
MAX_DICE=100
MAX_SIDES=1000
MAX_MULTIROLL=10

# Animation settings
ENABLE_ANIMATIONS=true
ANIMATION_DELAY=0.2

# Development features (set to true for development)
ENABLE_DEV_COMMANDS=false
ENABLE_HOT_RELOAD=false
```

## Development 🛠️

### Project Structure

```plaintext
dice-roller-bot/
├── bot/                 # Bot core functionality
│   ├── cog/            # Command groups (cogs)
│   │   ├── dice_rolling.py  # Main dice rolling commands
│   │   ├── help.py          # Help system
│   │   └── dev.py           # Development commands
│   └── utils/          # Utility functions
│       └── dice_parser.py   # Dice expression parser
├── config/             # Configuration management
│   └── config.py       # Environment variable handling
└── main.py            # Entry point
```

### Hot Reload Development Workflow

1. **Enable development mode** in your `.env`:

   ```plaintext
   ENABLE_DEV_COMMANDS=true
   ENABLE_HOT_RELOAD=true
   ```

2. **Start the bot** and use development commands:

   ```bash
   python main.py
   ```

3. **Available development commands**:
   - `!hotreload on` - Enable automatic code reloading
   - `!reload dice_rolling` - Manually reload a specific cog
   - `!watchstatus` - Check file watcher status
   - `!listcogs` - See all loaded cogs

4. **Make changes** to any file in:
   - `bot/cog/*.py` - Cogs will auto-reload
   - `bot/utils/*.py` - Utility changes trigger cog reloads
   - `config/*.py` - Config changes require bot restart

5. **See changes instantly** - Modified cogs reload automatically, and the bot sends a notification in Discord when hot reload occurs.

### Development Tips

- **Hot reload** watches file modification times and automatically reloads changed cogs
- **Manual reload** with `!reload` if you need more control
- **File watcher** runs every 2 seconds when enabled
- **Config changes** require a full bot restart to take effect
- **Dev commands** are owner-only for security

### Adding New Commands

1. Create a new cog in the `bot/cogs/` directory.
2. Implement your commands using `@commands.command()`
3. Add the cog to the bot in `main.py`:

   ```python
   async def setup_hook(self):
        """Load cogs"""
        cogs = ['bot.cog.dice_rolling', 'bot.cog.help', 'your.cog.name'] <- Add your cog here
   ```

#### Temporary commands can be added as cogs. Follow these steps:

1. Create a new cog in the `bot/cog/` directory:

   ```python
   import discord
   from discord.ext import commands

   class YourCog(commands.Cog):
       def __init__(self, bot):
           self.bot = bot
       
       @commands.command(name='yourcommand')
       async def your_command(self, ctx):
           await ctx.send("Hello from your new command!")

   async def setup(bot):
       await bot.add_cog(YourCog(bot))
   ```

2. The cog will be auto-loaded if hot reload is enabled, or use `!load your_cog`

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

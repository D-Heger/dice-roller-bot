import discord
from discord.ext import commands
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import Config

class Help(commands.Cog):
    """Custom help command"""
    
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = None
    
    def cog_unload(self):
        self.bot.help_command = self._original_help_command
    
    @commands.command(name='help', aliases=['h', 'commands'])
    async def help_command(self, ctx, command: str = None):
        """Show help for commands"""
        
        if command:
            # Show help for specific command
            cmd = self.bot.get_command(command)
            if not cmd:
                await ctx.send(f"❌ Command `{command}` not found.")
                return
            
            embed = discord.Embed(
                title=f"Help: {cmd.name}",
                description=cmd.help or "No description available.",
                color=discord.Color.blue()
            )
            
            if cmd.aliases:
                embed.add_field(
                    name="Aliases",
                    value=", ".join(f"`{alias}`" for alias in cmd.aliases),
                    inline=False
                )
            
            await ctx.send(embed=embed)
        else:
            # Show general help
            embed = discord.Embed(
                title="🎲 D&D Dice Bot Help",
                description="A feature-rich dice rolling bot for D&D 5e",
                color=discord.Color.blue()
            )
            
            # Group commands by category
            categories = {
                "🎲 Dice Rolling": [
                    ("roll [expression]", "Roll dice (e.g., 1d20+5)", "r"),
                    ("multiroll [times] [expression]", "Roll multiple times", "m"),
                ],
                "⚔️ D&D Specific": [
                    ("advantage [modifier]", "Roll with advantage", "adv"),
                    ("disadvantage [modifier]", "Roll with disadvantage", "dis"),
                    ("stats [system]", "Roll ability scores (dnd, adnd, pathfinder, heroic, standard, special, cortex)", None),
                ],
                "❓ Help": [
                    ("help [command]", "Show this help or command details", "h"),
                ],
            }
            
            # Add developer commands if enabled
            if Config.ENABLE_DEV_COMMANDS:
                categories["🔧 Developer"] = [
                    ("reload [cog]", "Reload cog(s) for development", None),
                    ("load [cog]", "Load a cog", None),
                    ("unload [cog]", "Unload a cog", None),
                    ("listcogs", "List all loaded cogs", None),
                    ("sync", "Sync slash commands", None),
                    ("hotreload [on/off]", "Toggle automatic code reloading", None),
                    ("watchstatus", "Show file watcher debug info", None),
                ]
            
            for category, commands in categories.items():
                value = []
                for cmd, desc, alias in commands:
                    if alias:
                        value.append(f"`!{cmd}` - {desc} (alias: `!{alias}`)")
                    else:
                        value.append(f"`!{cmd}` - {desc}")
                
                embed.add_field(
                    name=category,
                    value="\n".join(value),
                    inline=False
                )
            
            # Basic examples
            embed.add_field(
                name="📝 Basic Examples",
                value=(
                    "`!roll 1d20+5` - Roll a d20 with +5 modifier\n"
                    "`!roll 2d6+3` - Roll 2d6 and add 3\n"
                    "`!roll 1d8-2` - Roll 1d8 and subtract 2\n"
                    "`!adv +3` - Roll advantage with +3 modifier\n"
                    "`!dis -1` - Roll disadvantage with -1 modifier\n"
                    "`!stats` - Roll D&D 5e ability scores\n"
                    "`!stats pathfinder` - Roll Pathfinder ability scores"
                ),
                inline=False
            )
            
            # Advanced dice expressions
            embed.add_field(
                name="🎯 Advanced Expressions",
                value=(
                    "`!roll 2d6+1d4+2` - Multiple dice types with modifier\n"
                    "`!roll 3d8+2d6+5` - Complex damage roll\n"
                    "`!roll 1d100` - Percentile dice roll\n"
                    "`!m 6 4d6` - Roll 4d6 six times (for stats)\n"
                    "`!m 3 1d20+5` - Roll attack 3 times"
                ),
                inline=False
            )
            
            # Modifier examples
            embed.add_field(
                name="⚖️ Modifier Formats",
                value=(
                    "`+5` or `5` - Positive modifier\n"
                    "`-3` - Negative modifier\n"
                    "`+0` - No modifier (explicit)\n"
                    "**Note:** Modifiers work with advantage/disadvantage too!"
                ),
                inline=False
            )
            
            # Stat Systems
            embed.add_field(
                name="🎯 Stat Systems",
                value=(
                    "`!stats dnd` - D&D 5e (4d6 drop lowest)\n"
                    "`!stats adnd` - AD&D 2e (3d6 straight)\n"
                    "`!stats pathfinder` - Pathfinder style\n"
                    "`!stats heroic` - Heroic (2d6+6)\n"
                    "`!stats standard` - Standard array\n"
                    "`!stats special` - SPECIAL (Fallout)\n"
                    "`!stats cortex` - Cortex system dice"
                ),
                inline=False
            )
            
            # Expression format explanation
            embed.add_field(
                name="🔢 Expression Format",
                value=(
                    "`NdS±M` - Roll N dice with S sides, add/subtract M\n"
                    "• **N** = Number of dice (1-100)\n"
                    "• **S** = Sides per die (2-1000)\n"
                    "• **±M** = Modifier to add/subtract\n"
                    "• Can chain multiple dice: `1d20+2d6+3`"
                ),
                inline=False
            )
            
            embed.set_footer(text=f"Prefix: {self.bot.command_prefix} | Use !help [command] for more info")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
import discord
from discord.ext import commands

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
                    ("stats", "Roll ability scores", None),
                ],
                "❓ Help": [
                    ("help [command]", "Show this help or command details", "h"),
                ]
            }
            
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
            
            embed.add_field(
                name="📝 Examples",
                value=(
                    "`!roll 1d20+5` - Roll a d20 with +5 modifier\n"
                    "`!roll 2d6+1d4` - Roll 2d6 and 1d4\n"
                    "`!adv +3` - Roll advantage with +3\n"
                    "`!m 6 4d6k3` - Roll stats 6 times"
                ),
                inline=False
            )
            
            embed.set_footer(text=f"Prefix: {self.bot.command_prefix} | Use !help [command] for more info")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
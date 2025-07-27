import discord
from discord.ext import commands
import random
import logging
from typing import Optional

from ..utils.dice_parser import DiceParser
from config.config import Config

logger = logging.getLogger(__name__)

class DiceRolling(commands.Cog):
    """Dice rolling commands for D&D"""
    
    def __init__(self, bot):
        self.bot = bot
        self.parser = DiceParser(Config.MAX_DICE, Config.MAX_SIDES)
    
    @commands.command(name='roll', aliases=['r'])
    async def roll_dice(self, ctx, *, expression: str):
        """
        Roll dice with expressions like 1d20+5, 2d6, etc.
        
        Examples:
            !roll 1d20
            !roll 2d6+3
            !roll 1d20+1d4+2
        """
        try:
            parsed = self.parser.parse_expression(expression)
            if not parsed:
                raise ValueError("Invalid dice expression")
            
            result = self.parser.format_result(parsed)
            
            embed = discord.Embed(
                title="🎲 Dice Roll",
                color=discord.Color.blue()
            )
            embed.add_field(name="Expression", value=f"`{expression}`", inline=False)
            embed.add_field(name="Details", value=result['details'], inline=False)
            embed.add_field(name="Total", value=f"**{result['total']}**", inline=True)
            
            # Check for critical rolls on d20s
            for roll in result['rolls']:
                if roll['sides'] == 20 and roll['num_dice'] == 1:
                    if roll['rolls'][0] == 20:
                        embed.add_field(name="💫 Critical!", value="Natural 20!", inline=True)
                    elif roll['rolls'][0] == 1:
                        embed.add_field(name="💀 Critical Fail!", value="Natural 1!", inline=True)
            
            embed.set_footer(text=f"Rolled by {ctx.author.display_name}")
            await ctx.send(embed=embed)
            
        except ValueError as e:
            await ctx.send(f"❌ Error: {str(e)}")
            logger.warning(f"Invalid roll from {ctx.author}: {expression}")
        except Exception as e:
            await ctx.send("❌ An unexpected error occurred while rolling dice.")
            logger.error(f"Error in roll command: {str(e)}", exc_info=True)
    
    @commands.command(name='advantage', aliases=['adv'])
    async def roll_advantage(self, ctx, modifier: Optional[str] = "+0"):
        """Roll with advantage (2d20, take highest)"""
        try:
            # Parse modifier
            mod = self._parse_modifier(modifier)
            
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            highest = max(roll1, roll2)
            total = highest + mod
            
            embed = discord.Embed(
                title="🎲 Advantage Roll",
                color=discord.Color.green()
            )
            
            # Format rolls with emphasis on the chosen one
            if roll1 == highest:
                rolls_text = f"**{roll1}**, {roll2}"
            else:
                rolls_text = f"{roll1}, **{roll2}**"
            
            embed.add_field(name="Rolls", value=rolls_text, inline=True)
            embed.add_field(name="Modifier", value=f"{mod:+d}", inline=True)
            embed.add_field(name="Total", value=f"**{total}**", inline=True)
            
            if highest == 20:
                embed.add_field(name="💫 Critical!", value="Natural 20!", inline=False)
            elif highest == 1:
                embed.add_field(name="💀 Critical Fail!", value="Natural 1!", inline=False)
            
            embed.set_footer(text=f"Rolled by {ctx.author.display_name}")
            await ctx.send(embed=embed)
            
        except ValueError as e:
            await ctx.send(f"❌ Invalid modifier: {modifier}")
        except Exception as e:
            await ctx.send("❌ An error occurred while rolling.")
            logger.error(f"Error in advantage command: {str(e)}", exc_info=True)
    
    @commands.command(name='disadvantage', aliases=['dis'])
    async def roll_disadvantage(self, ctx, modifier: Optional[str] = "+0"):
        """Roll with disadvantage (2d20, take lowest)"""
        try:
            mod = self._parse_modifier(modifier)
            
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            lowest = min(roll1, roll2)
            total = lowest + mod
            
            embed = discord.Embed(
                title="🎲 Disadvantage Roll",
                color=discord.Color.red()
            )
            
            # Format rolls with emphasis on the chosen one
            if roll1 == lowest:
                rolls_text = f"**{roll1}**, {roll2}"
            else:
                rolls_text = f"{roll1}, **{roll2}**"
            
            embed.add_field(name="Rolls", value=rolls_text, inline=True)
            embed.add_field(name="Modifier", value=f"{mod:+d}", inline=True)
            embed.add_field(name="Total", value=f"**{total}**", inline=True)
            
            if lowest == 20:
                embed.add_field(name="💫 Critical!", value="Natural 20!", inline=False)
            elif lowest == 1:
                embed.add_field(name="💀 Critical Fail!", value="Natural 1!", inline=False)
            
            embed.set_footer(text=f"Rolled by {ctx.author.display_name}")
            await ctx.send(embed=embed)
            
        except ValueError as e:
            await ctx.send(f"❌ Invalid modifier: {modifier}")
        except Exception as e:
            await ctx.send("❌ An error occurred while rolling.")
            logger.error(f"Error in disadvantage command: {str(e)}", exc_info=True)
    
    @commands.command(name='stats')
    async def roll_stats(self, ctx):
        """Roll ability scores (4d6, drop lowest, 6 times)"""
        try:
            stats = []
            
            for i in range(6):
                rolls = sorted([random.randint(1, 6) for _ in range(4)], reverse=True)
                stat = sum(rolls[:3])
                stats.append((stat, rolls))
            
            embed = discord.Embed(
                title="📊 Ability Score Roll",
                description="Rolling 4d6, drop lowest, 6 times:",
                color=discord.Color.gold()
            )
            
            stat_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
            
            for i, ((stat, rolls), name) in enumerate(zip(stats, stat_names)):
                dropped = rolls[3]
                kept = rolls[:3]
                embed.add_field(
                    name=f"{name}",
                    value=f"{kept} ~~[{dropped}]~~\n**Total: {stat}**",
                    inline=True
                )
            
            total = sum(stat for stat, _ in stats)
            avg = total / 6
            
            embed.add_field(
                name="Summary",
                value=f"**Total: {total}** (Average: {avg:.1f})",
                inline=False
            )
            
            # Add a rating based on total
            if total >= 78:
                rating = "🌟 Exceptional!"
            elif total >= 72:
                rating = "✨ Great!"
            elif total >= 66:
                rating = "👍 Good"
            elif total >= 60:
                rating = "👌 Average"
            else:
                rating = "💪 Challenging"
            
            embed.add_field(name="Rating", value=rating, inline=False)
            embed.set_footer(text=f"Rolled by {ctx.author.display_name}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send("❌ An error occurred while rolling stats.")
            logger.error(f"Error in stats command: {str(e)}", exc_info=True)
    
    @commands.command(name='multiroll', aliases=['m'])
    async def multi_roll(self, ctx, times: int, *, expression: str):
        """Roll the same dice expression multiple times"""
        try:
            if times > Config.MAX_MULTIROLL:
                await ctx.send(f"❌ Maximum {Config.MAX_MULTIROLL} rolls at once!")
                return
            
            if times < 1:
                await ctx.send("❌ Must roll at least once!")
                return
            
            results = []
            
            for i in range(times):
                parsed = self.parser.parse_expression(expression)
                if not parsed:
                    raise ValueError("Invalid dice expression")
                
                result = self.parser.format_result(parsed)
                results.append(result['total'])
            
            embed = discord.Embed(
                title=f"🎲 Multi-Roll: {expression} × {times}",
                color=discord.Color.orange()
            )
            
            # Format results
            results_str = ", ".join(str(r) for r in results)
            if len(results_str) > 100:
                results_str = results_str[:97] + "..."
            
            embed.add_field(name="Results", value=results_str, inline=False)
            embed.add_field(name="Sum", value=f"{sum(results)}", inline=True)
            embed.add_field(name="Average", value=f"{sum(results)/len(results):.1f}", inline=True)
            embed.add_field(name="Min/Max", value=f"{min(results)} / {max(results)}", inline=True)
            
            embed.set_footer(text=f"Rolled by {ctx.author.display_name}")
            await ctx.send(embed=embed)
            
        except ValueError as e:
            await ctx.send(f"❌ Error: {str(e)}")
        except Exception as e:
            await ctx.send("❌ An error occurred while rolling.")
            logger.error(f"Error in multiroll command: {str(e)}", exc_info=True)
    
    def _parse_modifier(self, modifier: str) -> int:
        """Parse a modifier string into an integer"""
        if not modifier:
            return 0
        
        # Remove spaces
        modifier = modifier.strip()
        
        # Handle different formats
        if modifier[0] in ['+', '-']:
            return int(modifier)
        else:
            return int(modifier)

async def setup(bot):
    await bot.add_cog(DiceRolling(bot))
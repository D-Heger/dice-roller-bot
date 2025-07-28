import discord
from discord.ext import commands
import random
import logging
import asyncio
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
            
            # Create initial animation embed if animations are enabled
            if Config.ENABLE_ANIMATIONS:
                # Show rolling animation
                rolling_embed = discord.Embed(
                    title="🎲 Rolling Dice...",
                    description=f"Rolling `{expression}`",
                    color=discord.Color.orange()
                )
                rolling_embed.add_field(name="Status", value="...🎲...", inline=False)
                message = await ctx.send(embed=rolling_embed)
                
                # Enhanced animation frames showing dice rolling
                animation_frames = [
                    {"emoji": "🎲💨", "color": discord.Color.orange()},
                    {"emoji": "🎯🎲", "color": discord.Color.red()},
                    {"emoji": "🎲⚡", "color": discord.Color.gold()},
                    {"emoji": "🌟🎲", "color": discord.Color.green()},
                    {"emoji": "🎲✨", "color": discord.Color.blue()},
                    {"emoji": "💫🎲", "color": discord.Color.purple()},
                ]
                
                # Animate for a few frames with proper timing
                for frame in animation_frames:
                    rolling_embed.colour = frame["color"]
                    rolling_embed.set_field_at(0, name="Status", value=frame["emoji"], inline=False)
                    await message.edit(embed=rolling_embed)
                    await asyncio.sleep(Config.ANIMATION_DELAY)
            
            # Calculate the actual result
            result = self.parser.format_result(parsed)
            
            # Create the final result embed
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
            
            # Update the message with final result if animation was shown, otherwise send new message
            if Config.ENABLE_ANIMATIONS and 'message' in locals():
                await message.edit(embed=embed)
            else:
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
    async def roll_stats(self, ctx, system: Optional[str] = "dnd"):
        """Roll ability scores using different systems (dnd, adnd, pathfinder, heroic, standard)"""
        try:
            system = system.lower().strip()
            
            # Define stat rolling systems
            stat_systems = {
                "dnd": {
                    "name": "D&D 5e Standard",
                    "description": "4d6, drop lowest",
                    "method": lambda: self._roll_4d6_drop_lowest(),
                    "rating_thresholds": [78, 72, 66, 60]
                },
                "adnd": {
                    "name": "AD&D 2e Method I",
                    "description": "3d6 straight",
                    "method": lambda: self._roll_3d6(),
                    "rating_thresholds": [72, 66, 60, 54]
                },
                "pathfinder": {
                    "name": "Pathfinder Point Buy Equivalent",
                    "description": "4d6, drop lowest, reroll if total < 70",
                    "method": lambda: self._roll_pathfinder_style(),
                    "rating_thresholds": [78, 74, 70, 66]
                },
                "heroic": {
                    "name": "Heroic Array",
                    "description": "2d6+6 for each stat",
                    "method": lambda: self._roll_heroic(),
                    "rating_thresholds": [84, 78, 72, 66]
                },
                "standard": {
                    "name": "Standard Array",
                    "description": "Fixed values: 15, 14, 13, 12, 10, 8",
                    "method": lambda: self._roll_standard_array(),
                    "rating_thresholds": [72, 72, 72, 72]  # Always the same
                },
                "special": {
                    "name": "SPECIAL System (Fallout)",
                    "description": "5 + 1d5 for each SPECIAL stat",
                    "method": lambda: self._roll_special(),
                    "rating_thresholds": [49, 45, 42, 39]
                },
                "cortex": {
                    "name": "Cortex System",
                    "description": "Dice steps: d4, d6, d8, d10, d12 distributed",
                    "method": lambda: self._roll_cortex(),
                    "rating_thresholds": [54, 48, 42, 36]  # Based on average die values
                }
            }
            
            if system not in stat_systems:
                available = ", ".join(stat_systems.keys())
                await ctx.send(f"❌ Unknown system `{system}`. Available: {available}")
                return
            
            system_info = stat_systems[system]
            stats = []
            
            # Roll stats based on the system
            num_stats = 7 if system == "special" else 6
            for _ in range(num_stats):
                stat_data = system_info["method"]()
                stats.append(stat_data)
            
            embed = discord.Embed(
                title=f"📊 {system_info['name']}",
                description=f"{system_info['description']}",
                color=discord.Color.gold()
            )
            
            # Choose stat names based on system
            if system == "special":
                stat_names = ["STR", "PER", "END", "CHA", "INT", "AGI", "LCK"]
            else:
                stat_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
            
            for _, (stat_data, name) in enumerate(zip(stats, stat_names)):
                if system == "standard":
                    embed.add_field(
                        name=f"{name}",
                        value=f"**Total: {stat_data['total']}**",
                        inline=True
                    )
                elif system == "cortex":
                    embed.add_field(
                        name=f"{name}",
                        value=f"{stat_data['rolls'][0]}\n**Total: {stat_data['total']}**",
                        inline=True
                    )
                else:
                    if 'dropped' in stat_data:
                        embed.add_field(
                            name=f"{name}",
                            value=f"{stat_data['kept']} ~~[{stat_data['dropped']}]~~\n**Total: {stat_data['total']}**",
                            inline=True
                        )
                    else:
                        embed.add_field(
                            name=f"{name}",
                            value=f"{stat_data['rolls']}\n**Total: {stat_data['total']}**",
                            inline=True
                        )
            
            total = sum(stat['total'] for stat in stats)
            avg = total / len(stats)
            
            embed.add_field(
                name="Summary",
                value=f"**Total: {total}** (Average: {avg:.1f})",
                inline=False
            )
            
            # Add a rating based on total and system
            thresholds = system_info["rating_thresholds"]
            if total >= thresholds[0]:
                rating = "🌟 Exceptional!"
            elif total >= thresholds[1]:
                rating = "✨ Great!"
            elif total >= thresholds[2]:
                rating = "👍 Good"
            elif total >= thresholds[3]:
                rating = "👌 Average"
            else:
                rating = "💪 Challenging"
            
            embed.add_field(name="Rating", value=rating, inline=False)
            embed.set_footer(text=f"Rolled by {ctx.author.display_name} | System: {system}")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send("❌ An error occurred while rolling stats.")
            logger.error(f"Error in stats command: {str(e)}", exc_info=True)
    
    def _roll_4d6_drop_lowest(self):
        """Roll 4d6, drop lowest"""
        rolls = sorted([random.randint(1, 6) for _ in range(4)], reverse=True)
        return {
            'total': sum(rolls[:3]),
            'kept': rolls[:3],
            'dropped': rolls[3]
        }
    
    def _roll_3d6(self):
        """Roll 3d6 straight"""
        rolls = [random.randint(1, 6) for _ in range(3)]
        return {
            'total': sum(rolls),
            'rolls': rolls
        }
    
    def _roll_pathfinder_style(self):
        """Roll 4d6 drop lowest, but ensure reasonable stats"""
        rolls = sorted([random.randint(1, 6) for _ in range(4)], reverse=True)
        return {
            'total': sum(rolls[:3]),
            'kept': rolls[:3],
            'dropped': rolls[3]
        }
    
    def _roll_heroic(self):
        """Roll 2d6+6 for heroic characters"""
        rolls = [random.randint(1, 6) for _ in range(2)]
        total = sum(rolls) + 6
        return {
            'total': total,
            'rolls': rolls + [6]  # Show the +6 bonus
        }
    
    def _roll_standard_array(self):
        """Return standard array values in random order"""
        if not hasattr(self, '_standard_values'):
            self._standard_values = [15, 14, 13, 12, 10, 8]
            random.shuffle(self._standard_values)
        
        if not self._standard_values:
            self._standard_values = [15, 14, 13, 12, 10, 8]
            random.shuffle(self._standard_values)
        
        value = self._standard_values.pop()
        return {
            'total': value
        }
    
    def _roll_special(self):
        """Roll SPECIAL stats: 5 + 1d5"""
        roll = random.randint(1, 5)
        total = 5 + roll
        return {
            'total': total,
            'rolls': [5, roll]  # Show base 5 + roll
        }
    
    def _roll_cortex(self):
        """Roll Cortex system dice steps"""
        if not hasattr(self, '_cortex_dice'):
            self._cortex_dice = [4, 6, 8, 10, 12, 6]  # d4, d6, d8, d10, d12, extra d6
            random.shuffle(self._cortex_dice)
        
        if not self._cortex_dice:
            self._cortex_dice = [4, 6, 8, 10, 12, 6]
            random.shuffle(self._cortex_dice)
        
        die_size = self._cortex_dice.pop()
        roll = random.randint(1, die_size)
        return {
            'total': roll,
            'rolls': [f"d{die_size}: {roll}"]
        }
    
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
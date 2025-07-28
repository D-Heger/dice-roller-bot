import discord
from discord.ext import commands
import json
import os
import random
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class Characters(commands.Cog):
    """Character management with persistence"""
    
    def __init__(self, bot):
        self.bot = bot
        self.data_dir = Path("data/characters")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_server_file(self, guild_id: int) -> Path:
        """Get the JSON file path for a specific server"""
        return self.data_dir / f"{guild_id}.json"
    
    def _load_characters(self, guild_id: int) -> Dict[str, Dict[str, Any]]:
        """Load characters for a specific server"""
        file_path = self._get_server_file(guild_id)
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading characters for guild {guild_id}: {e}")
        return {}
    
    def _save_characters(self, guild_id: int, characters: Dict[str, Dict[str, Any]]) -> bool:
        """Save characters for a specific server"""
        file_path = self._get_server_file(guild_id)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(characters, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            logger.error(f"Error saving characters for guild {guild_id}: {e}")
            return False
    
    def _get_user_key(self, user_id: int) -> str:
        """Get the key for storing user characters"""
        return str(user_id)
    
    def _generate_stats(self, system: str) -> Dict[str, int]:
        """Generate stats using the specified system"""
        stat_systems = {
            "dnd": lambda: self._roll_4d6_drop_lowest(),
            "adnd": lambda: self._roll_3d6(),
            "pathfinder": lambda: self._roll_4d6_drop_lowest(),
            "heroic": lambda: self._roll_heroic(),
            "standard": lambda: self._get_standard_array(),
            "special": lambda: self._roll_special(),
            "cortex": lambda: self._roll_cortex()
        }
        
        if system not in stat_systems:
            system = "dnd"  # Default fallback
        
        method = stat_systems[system]
        
        if system == "special":
            stat_names = ["STR", "PER", "END", "CHA", "INT", "AGI", "LCK"]
        else:
            stat_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
        
        stats = {}
        for stat in stat_names:
            stats[stat] = method()
        
        return stats
    
    def _roll_4d6_drop_lowest(self) -> int:
        """Roll 4d6, drop lowest"""
        rolls = sorted([random.randint(1, 6) for _ in range(4)], reverse=True)
        return sum(rolls[:3])
    
    def _roll_3d6(self) -> int:
        """Roll 3d6 straight"""
        return sum(random.randint(1, 6) for _ in range(3))
    
    def _roll_heroic(self) -> int:
        """Roll 2d6+6 for heroic characters"""
        return sum(random.randint(1, 6) for _ in range(2)) + 6
    
    def _get_standard_array(self) -> int:
        """Return standard array values"""
        if not hasattr(self, '_standard_values'):
            self._standard_values = [15, 14, 13, 12, 10, 8]
            random.shuffle(self._standard_values)
        
        if not self._standard_values:
            self._standard_values = [15, 14, 13, 12, 10, 8]
            random.shuffle(self._standard_values)
        
        return self._standard_values.pop()
    
    def _roll_special(self) -> int:
        """Roll SPECIAL stats: 5 + 1d5"""
        return 5 + random.randint(1, 5)
    
    def _roll_cortex(self) -> int:
        """Roll Cortex system dice steps"""
        if not hasattr(self, '_cortex_dice'):
            self._cortex_dice = [4, 6, 8, 10, 12, 6]
            random.shuffle(self._cortex_dice)
        
        if not self._cortex_dice:
            self._cortex_dice = [4, 6, 8, 10, 12, 6]
            random.shuffle(self._cortex_dice)
        
        die_size = self._cortex_dice.pop()
        return random.randint(1, die_size)
    
    @commands.group(name='char', aliases=['character'], invoke_without_command=True)
    async def character(self, ctx, character_name: str = None):
        """Character management commands. Use !char <name> to view a character."""
        if character_name:
            await self.show_character(ctx, character_name=character_name)
        else:
            await self.list_characters(ctx)
    
    @character.command(name='create')
    async def create_character(self, ctx, name: str, *, role: str = "Adventurer"):
        """Create a new character: !char create "Gandalf" Wizard"""
        characters = self._load_characters(ctx.guild.id)
        user_key = self._get_user_key(ctx.author.id)
        
        if user_key not in characters:
            characters[user_key] = {}
        
        # Check if character already exists
        name_lower = name.lower()
        if any(char['name'].lower() == name_lower for char in characters[user_key].values()):
            await ctx.send(f"❌ You already have a character named '{name}'!")
            return
        
        # Generate unique character ID
        char_id = f"{ctx.author.id}_{len(characters[user_key])}"
        
        # Create character with default D&D stats
        character_data = {
            "name": name,
            "nickname": None,
            "role": role,
            "system": "dnd",
            "stats": self._generate_stats("dnd"),
            "backstory": None,
            "notes": [],
            "created_by": ctx.author.id,
            "created_at": ctx.message.created_at.isoformat()
        }
        
        characters[user_key][char_id] = character_data
        
        if self._save_characters(ctx.guild.id, characters):
            embed = discord.Embed(
                title="✨ Character Created!",
                description=f"**{name}** the {role}",
                color=discord.Color.green()
            )
            
            # Show stats
            stats_text = "\n".join([f"**{stat}**: {value}" for stat, value in character_data['stats'].items()])
            embed.add_field(name="Stats (D&D 5e)", value=stats_text, inline=True)
            
            embed.set_footer(text=f"Created by {ctx.author.display_name} | Use !char modify to customize")
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to save character. Please try again.")
    
    @character.command(name='list')
    async def list_characters(self, ctx, user: Optional[discord.Member] = None):
        """List all characters for a user"""
        target_user = user or ctx.author
        characters = self._load_characters(ctx.guild.id)
        user_key = self._get_user_key(target_user.id)
        
        if user_key not in characters or not characters[user_key]:
            if target_user == ctx.author:
                await ctx.send("You don't have any characters yet! Use `!char create` to make one.")
            else:
                await ctx.send(f"{target_user.display_name} doesn't have any characters.")
            return
        
        embed = discord.Embed(
            title=f"🎭 {target_user.display_name}'s Characters",
            color=discord.Color.blue()
        )
        
        for char_id, char_data in characters[user_key].items():
            name = char_data['name']
            nickname = f" ({char_data['nickname']})" if char_data['nickname'] else ""
            role = char_data['role']
            system = char_data['system'].upper()
            
            embed.add_field(
                name=f"{name}{nickname}",
                value=f"**Role**: {role}\n**System**: {system}",
                inline=True
            )
        
        embed.set_footer(text=f"Use !char <name> to view details")
        await ctx.send(embed=embed)
    
    @character.command(name='show')
    async def show_character(self, ctx, *, character_name: str):
        """Show detailed character information"""
        characters = self._load_characters(ctx.guild.id)
        user_key = self._get_user_key(ctx.author.id)
        
        if user_key not in characters:
            await ctx.send("You don't have any characters!")
            return
        
        # Find character (case insensitive)
        character_data = None
        for char_data in characters[user_key].values():
            if (char_data['name'].lower() == character_name.lower() or 
                (char_data['nickname'] and char_data['nickname'].lower() == character_name.lower())):
                character_data = char_data
                break
        
        if not character_data:
            await ctx.send(f"❌ Character '{character_name}' not found!")
            return
        
        # Create detailed embed
        name = character_data['name']
        nickname = f" ({character_data['nickname']})" if character_data['nickname'] else ""
        
        embed = discord.Embed(
            title=f"🎭 {name}{nickname}",
            description=f"**Role**: {character_data['role']}",
            color=discord.Color.purple()
        )
        
        # Stats
        stats_text = "\n".join([f"**{stat}**: {value}" for stat, value in character_data['stats'].items()])
        embed.add_field(
            name=f"Stats ({character_data['system'].upper()})",
            value=stats_text,
            inline=True
        )
        
        # Backstory
        if character_data['backstory']:
            backstory = character_data['backstory']
            if len(backstory) > 200:
                backstory = backstory[:197] + "..."
            embed.add_field(name="Backstory", value=backstory, inline=False)
        
        # Notes
        if character_data['notes']:
            notes_text = "\n".join([f"• {note}" for note in character_data['notes'][-3:]])  # Show last 3 notes
            if len(character_data['notes']) > 3:
                notes_text += f"\n... and {len(character_data['notes']) - 3} more"
            embed.add_field(name="Notes", value=notes_text, inline=False)
        
        embed.set_footer(text=f"Created {character_data['created_at'][:10]}")
        await ctx.send(embed=embed)
    
    @character.command(name='delete')
    async def delete_character(self, ctx, *, character_name: str):
        """Delete a character"""
        characters = self._load_characters(ctx.guild.id)
        user_key = self._get_user_key(ctx.author.id)
        
        if user_key not in characters:
            await ctx.send("You don't have any characters!")
            return
        
        # Find and remove character
        char_to_delete = None
        for char_id, char_data in characters[user_key].items():
            if (char_data['name'].lower() == character_name.lower() or 
                (char_data['nickname'] and char_data['nickname'].lower() == character_name.lower())):
                char_to_delete = char_id
                break
        
        if not char_to_delete:
            await ctx.send(f"❌ Character '{character_name}' not found!")
            return
        
        deleted_char = characters[user_key].pop(char_to_delete)
        
        if self._save_characters(ctx.guild.id, characters):
            await ctx.send(f"🗑️ Character '{deleted_char['name']}' has been deleted.")
        else:
            # Restore character if save failed
            characters[user_key][char_to_delete] = deleted_char
            await ctx.send("❌ Failed to delete character. Please try again.")
    
    @character.group(name='modify', aliases=['mod'], invoke_without_command=True)
    async def modify_character(self, ctx):
        """Character modification commands"""
        await ctx.send("Use `!char modify <subcommand>`. Available: name, nickname, role, system, backstory")
    
    @modify_character.command(name='name')
    async def modify_name(self, ctx, current_name: str, *, new_name: str):
        """Change a character's name: !char modify name "Old Name" "New Name" """
        characters = self._load_characters(ctx.guild.id)
        user_key = self._get_user_key(ctx.author.id)
        
        if user_key not in characters:
            await ctx.send("You don't have any characters!")
            return
        
        # Find character
        char_data = None
        for char in characters[user_key].values():
            if char['name'].lower() == current_name.lower():
                char_data = char
                break
        
        if not char_data:
            await ctx.send(f"❌ Character '{current_name}' not found!")
            return
        
        # Check if new name already exists
        if any(char['name'].lower() == new_name.lower() for char in characters[user_key].values() if char != char_data):
            await ctx.send(f"❌ You already have a character named '{new_name}'!")
            return
        
        old_name = char_data['name']
        char_data['name'] = new_name
        
        if self._save_characters(ctx.guild.id, characters):
            await ctx.send(f"✅ Character renamed from '{old_name}' to '{new_name}'")
        else:
            char_data['name'] = old_name  # Revert
            await ctx.send("❌ Failed to save changes. Please try again.")
    
    @modify_character.command(name='nickname')
    async def modify_nickname(self, ctx, character_name: str, *, nickname: str = None):
        """Set or clear a character's nickname: !char modify nickname "Name" "Nick" """
        characters = self._load_characters(ctx.guild.id)
        user_key = self._get_user_key(ctx.author.id)
        
        char_data = self._find_character(characters, user_key, character_name)
        if not char_data:
            await ctx.send(f"❌ Character '{character_name}' not found!")
            return
        
        if nickname and nickname.lower() in ['clear', 'remove', 'none']:
            nickname = None
        
        char_data['nickname'] = nickname
        
        if self._save_characters(ctx.guild.id, characters):
            if nickname:
                await ctx.send(f"✅ '{char_data['name']}' nickname set to '{nickname}'")
            else:
                await ctx.send(f"✅ Cleared nickname for '{char_data['name']}'")
        else:
            await ctx.send("❌ Failed to save changes. Please try again.")
    
    @modify_character.command(name='role')
    async def modify_role(self, ctx, character_name: str, *, new_role: str):
        """Change a character's role: !char modify role "Name" "New Role" """
        characters = self._load_characters(ctx.guild.id)
        user_key = self._get_user_key(ctx.author.id)
        
        char_data = self._find_character(characters, user_key, character_name)
        if not char_data:
            await ctx.send(f"❌ Character '{character_name}' not found!")
            return
        
        old_role = char_data['role']
        char_data['role'] = new_role
        
        if self._save_characters(ctx.guild.id, characters):
            await ctx.send(f"✅ '{char_data['name']}' role changed from '{old_role}' to '{new_role}'")
        else:
            char_data['role'] = old_role  # Revert
            await ctx.send("❌ Failed to save changes. Please try again.")
    
    @modify_character.command(name='system')
    async def modify_system(self, ctx, character_name: str, new_system: str, regenerate: str = "no"):
        """Change character's stat system: !char modify system "Name" dnd [yes/no to regenerate]"""
        valid_systems = ["dnd", "adnd", "pathfinder", "heroic", "standard", "special", "cortex"]
        
        if new_system.lower() not in valid_systems:
            await ctx.send(f"❌ Invalid system. Available: {', '.join(valid_systems)}")
            return
        
        characters = self._load_characters(ctx.guild.id)
        user_key = self._get_user_key(ctx.author.id)
        
        char_data = self._find_character(characters, user_key, character_name)
        if not char_data:
            await ctx.send(f"❌ Character '{character_name}' not found!")
            return
        
        old_system = char_data['system']
        old_stats = char_data['stats'].copy()
        
        char_data['system'] = new_system.lower()
        
        # Regenerate stats if requested
        if regenerate.lower() in ['yes', 'y', 'true', '1']:
            char_data['stats'] = self._generate_stats(new_system.lower())
            stats_msg = " and regenerated stats"
        else:
            stats_msg = " (stats kept)"
        
        if self._save_characters(ctx.guild.id, characters):
            await ctx.send(f"✅ '{char_data['name']}' system changed from '{old_system}' to '{new_system}'{stats_msg}")
        else:
            char_data['system'] = old_system  # Revert
            char_data['stats'] = old_stats
            await ctx.send("❌ Failed to save changes. Please try again.")
    
    @character.command(name='backstory')
    async def set_backstory(self, ctx, character_name: str, *, backstory: str = None):
        """Set or view character backstory: !char backstory "Name" "Their story..." """
        characters = self._load_characters(ctx.guild.id)
        user_key = self._get_user_key(ctx.author.id)
        
        char_data = self._find_character(characters, user_key, character_name)
        if not char_data:
            await ctx.send(f"❌ Character '{character_name}' not found!")
            return
        
        if backstory is None:
            # Show current backstory
            if char_data['backstory']:
                embed = discord.Embed(
                    title=f"📖 {char_data['name']}'s Backstory",
                    description=char_data['backstory'],
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"'{char_data['name']}' doesn't have a backstory yet.")
            return
        
        if backstory.lower() in ['clear', 'remove', 'none']:
            char_data['backstory'] = None
            message = f"✅ Cleared backstory for '{char_data['name']}'"
        else:
            char_data['backstory'] = backstory
            message = f"✅ Set backstory for '{char_data['name']}'"
        
        if self._save_characters(ctx.guild.id, characters):
            await ctx.send(message)
        else:
            await ctx.send("❌ Failed to save changes. Please try again.")
    
    @character.command(name='note')
    async def add_note(self, ctx, character_name: str, *, note: str):
        """Add a note to a character: !char note "Name" "Note text" """
        characters = self._load_characters(ctx.guild.id)
        user_key = self._get_user_key(ctx.author.id)
        
        char_data = self._find_character(characters, user_key, character_name)
        if not char_data:
            await ctx.send(f"❌ Character '{character_name}' not found!")
            return
        
        if 'notes' not in char_data:
            char_data['notes'] = []
        
        char_data['notes'].append(note)
        
        if self._save_characters(ctx.guild.id, characters):
            await ctx.send(f"✅ Added note to '{char_data['name']}' (Total: {len(char_data['notes'])} notes)")
        else:
            char_data['notes'].pop()  # Remove the note we just added
            await ctx.send("❌ Failed to save note. Please try again.")
    
    @character.command(name='notes')
    async def list_notes(self, ctx, character_name: str, page: int = 1):
        """List all notes for a character: !char notes "Name" [page]"""
        characters = self._load_characters(ctx.guild.id)
        user_key = self._get_user_key(ctx.author.id)
        
        char_data = self._find_character(characters, user_key, character_name)
        if not char_data:
            await ctx.send(f"❌ Character '{character_name}' not found!")
            return
        
        if not char_data.get('notes'):
            await ctx.send(f"'{char_data['name']}' doesn't have any notes yet.")
            return
        
        notes_per_page = 5
        total_notes = len(char_data['notes'])
        total_pages = (total_notes + notes_per_page - 1) // notes_per_page
        
        if page < 1 or page > total_pages:
            await ctx.send(f"❌ Page {page} doesn't exist. Available pages: 1-{total_pages}")
            return
        
        start_idx = (page - 1) * notes_per_page
        end_idx = min(start_idx + notes_per_page, total_notes)
        
        embed = discord.Embed(
            title=f"📝 {char_data['name']}'s Notes",
            color=discord.Color.blue()
        )
        
        for i in range(start_idx, end_idx):
            embed.add_field(
                name=f"Note {i + 1}",
                value=char_data['notes'][i],
                inline=False
            )
        
        embed.set_footer(text=f"Page {page}/{total_pages} • {total_notes} total notes")
        await ctx.send(embed=embed)
    
    @character.command(name='clearnotes')
    async def clear_notes(self, ctx, character_name: str):
        """Clear all notes for a character: !char clearnotes "Name" """
        characters = self._load_characters(ctx.guild.id)
        user_key = self._get_user_key(ctx.author.id)
        
        char_data = self._find_character(characters, user_key, character_name)
        if not char_data:
            await ctx.send(f"❌ Character '{character_name}' not found!")
            return
        
        note_count = len(char_data.get('notes', []))
        char_data['notes'] = []
        
        if self._save_characters(ctx.guild.id, characters):
            await ctx.send(f"✅ Cleared {note_count} notes from '{char_data['name']}'")
        else:
            await ctx.send("❌ Failed to clear notes. Please try again.")
    
    def _find_character(self, characters: dict, user_key: str, character_name: str) -> Optional[Dict[str, Any]]:
        """Helper to find a character by name or nickname"""
        if user_key not in characters:
            return None
        
        for char_data in characters[user_key].values():
            if (char_data['name'].lower() == character_name.lower() or 
                (char_data['nickname'] and char_data['nickname'].lower() == character_name.lower())):
                return char_data
        return None

async def setup(bot):
    await bot.add_cog(Characters(bot))
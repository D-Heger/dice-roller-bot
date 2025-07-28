import discord
from discord.ext import commands, tasks
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import Config

logger = logging.getLogger(__name__)

class Development(commands.Cog):
    """Development commands for hot reloading"""
    
    def __init__(self, bot):
        self.bot = bot
        self.file_timestamps = {}
        
        if Config.ENABLE_HOT_RELOAD:
            self.file_watcher.start()
            logger.info("Hot reload file watcher started")
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        if hasattr(self, 'file_watcher'):
            self.file_watcher.cancel()
    
    @tasks.loop(seconds=2.0)
    async def file_watcher(self):
        """Watch for file changes and auto-reload cogs"""
        try:
            bot_dir = Path(__file__).parent.parent
            cog_files = list(bot_dir.glob("cog/*.py"))
            utils_files = list(bot_dir.glob("utils/*.py"))
            config_files = list(bot_dir.parent.glob("config/*.py"))
            
            all_files = cog_files + utils_files + config_files
            
            # Debug: Log watched files on first run
            if not hasattr(self, '_debug_logged'):
                logger.info(f"File watcher monitoring {len(all_files)} files:")
                for f in all_files:
                    logger.info(f"  - {f}")
                self._debug_logged = True
            
            for file_path in all_files:
                if not file_path.exists():
                    continue
                    
                current_mtime = file_path.stat().st_mtime
                file_key = str(file_path)
                
                if file_key not in self.file_timestamps:
                    self.file_timestamps[file_key] = current_mtime
                    continue
                
                if current_mtime > self.file_timestamps[file_key]:
                    old_mtime = self.file_timestamps[file_key]
                    self.file_timestamps[file_key] = current_mtime
                    
                    logger.info(f"File change detected: {file_path.name} (mtime: {old_mtime} -> {current_mtime})")
                    
                    # Determine which cog to reload based on file
                    if file_path.parent.name == "cog" and file_path.stem != "__init__":
                        cog_name = f"bot.cog.{file_path.stem}"
                        if cog_name in self.bot.extensions and cog_name != "bot.cog.dev":
                            try:
                                logger.info(f"Attempting to reload {cog_name}...")
                                await self.bot.reload_extension(cog_name)
                                logger.info(f"✅ Auto-reloaded {cog_name} due to file change")                    
                            except Exception as e:
                                logger.error(f"❌ Auto-reload failed for {cog_name}: {e}")
                    
                    # For config changes, log but don't auto-reload (requires restart)
                    elif file_path.parent.name == "config":
                        logger.info(f"Config file {file_path.name} changed - restart bot to apply changes")
                        
        except Exception as e:
            logger.error(f"Error in file watcher: {e}")
    
    @file_watcher.before_loop
    async def before_file_watcher(self):
        """Wait until bot is ready before starting file watcher"""
        await self.bot.wait_until_ready()
    
    @commands.command(name='reload')
    @commands.is_owner()
    async def reload_cog(self, ctx, *, cog_name: str = None):
        """
        Reload a specific cog or all cogs
        Usage: !reload [cog_name]
        """
        try:
            if cog_name is None:
                # Reload all cogs
                cogs = list(self.bot.extensions.keys())
                reloaded = []
                failed = []
                
                for cog in cogs:
                    if cog == 'bot.cog.dev':  # Don't reload dev cog
                        continue
                    try:
                        await self.bot.reload_extension(cog)
                        reloaded.append(cog)
                        logger.info(f"Reloaded cog: {cog}")
                    except Exception as e:
                        failed.append(f"{cog}: {str(e)}")
                        logger.error(f"Failed to reload {cog}: {e}")
                
                embed = discord.Embed(
                    title="🔄 Cog Reload Results",
                    color=discord.Color.green() if not failed else discord.Color.orange()
                )
                
                if reloaded:
                    embed.add_field(
                        name="✅ Reloaded",
                        value="\n".join(f"`{cog}`" for cog in reloaded),
                        inline=False
                    )
                
                if failed:
                    embed.add_field(
                        name="❌ Failed",
                        value="\n".join(f"`{fail}`" for fail in failed),
                        inline=False
                    )
                
                await ctx.send(embed=embed)
                
            else:
                # Reload specific cog
                cog_path = f"bot.cog.{cog_name}" if not cog_name.startswith('bot.cog.') else cog_name
                
                if cog_path not in self.bot.extensions:
                    await ctx.send(f"❌ Cog `{cog_path}` is not loaded")
                    return
                
                await self.bot.reload_extension(cog_path)
                logger.info(f"Reloaded cog: {cog_path}")
                
                embed = discord.Embed(
                    title="🔄 Cog Reloaded",
                    description=f"Successfully reloaded `{cog_path}`",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error reloading cog: {e}")
            await ctx.send(f"❌ Error reloading cog: {str(e)}")
    
    @commands.command(name='load')
    @commands.is_owner()
    async def load_cog(self, ctx, *, cog_name: str):
        """
        Load a cog
        Usage: !load cog_name
        """
        try:
            cog_path = f"bot.cog.{cog_name}" if not cog_name.startswith('bot.cog.') else cog_name
            
            if cog_path in self.bot.extensions:
                await ctx.send(f"❌ Cog `{cog_path}` is already loaded")
                return
            
            await self.bot.load_extension(cog_path)
            logger.info(f"Loaded cog: {cog_path}")
            
            embed = discord.Embed(
                title="✅ Cog Loaded",
                description=f"Successfully loaded `{cog_path}`",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error loading cog: {e}")
            await ctx.send(f"❌ Error loading cog: {str(e)}")
    
    @commands.command(name='unload')
    @commands.is_owner()
    async def unload_cog(self, ctx, *, cog_name: str):
        """
        Unload a cog
        Usage: !unload cog_name
        """
        try:
            cog_path = f"bot.cog.{cog_name}" if not cog_name.startswith('bot.cog.') else cog_name
            
            if cog_path == 'bot.cog.dev':
                await ctx.send("❌ Cannot unload development cog")
                return
            
            if cog_path not in self.bot.extensions:
                await ctx.send(f"❌ Cog `{cog_path}` is not loaded")
                return
            
            await self.bot.unload_extension(cog_path)
            logger.info(f"Unloaded cog: {cog_path}")
            
            embed = discord.Embed(
                title="🚫 Cog Unloaded",
                description=f"Successfully unloaded `{cog_path}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error unloading cog: {e}")
            await ctx.send(f"❌ Error unloading cog: {str(e)}")
    
    @commands.command(name='listcogs')
    @commands.is_owner()
    async def list_cogs(self, ctx):
        """List all loaded cogs"""
        cogs = list(self.bot.extensions.keys())
        
        embed = discord.Embed(
            title="📋 Loaded Cogs",
            color=discord.Color.blue()
        )
        
        if cogs:
            embed.description = "\n".join(f"`{cog}`" for cog in sorted(cogs))
        else:
            embed.description = "No cogs loaded"
        
        await ctx.send(embed=embed)
    
    @commands.command(name='sync')
    @commands.is_owner()
    async def sync_commands(self, ctx):
        """Sync slash commands (if any)"""
        try:
            synced = await self.bot.tree.sync()
            embed = discord.Embed(
                title="🔄 Commands Synced",
                description=f"Synced {len(synced)} command(s)",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error syncing commands: {str(e)}")
    
    @commands.command(name='watchstatus')
    @commands.is_owner()
    async def watch_status(self, ctx):
        """Show file watcher status and debug info"""
        embed = discord.Embed(title="🔍 File Watcher Debug Info", color=discord.Color.blue())
        
        # Watcher status
        is_running = hasattr(self, 'file_watcher') and self.file_watcher.is_running()
        embed.add_field(name="Status", value="Running" if is_running else "Stopped", inline=True)
        
        if is_running:
            embed.add_field(name="Loop Count", value=str(self.file_watcher.current_loop), inline=True)
        
        # Watched files count
        embed.add_field(name="Tracked Files", value=str(len(self.file_timestamps)), inline=True)
        
        # Show some tracked files
        if self.file_timestamps:
            file_list = []
            for file_path, mtime in list(self.file_timestamps.items())[:5]:
                path_obj = Path(file_path)
                file_list.append(f"`{path_obj.name}` (mtime: {mtime})")
            
            embed.add_field(
                name="Sample Files",
                value="\n".join(file_list) + ("..." if len(self.file_timestamps) > 5 else ""),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='hotreload')
    @commands.is_owner()
    async def toggle_hot_reload(self, ctx, enable: str = None):
        """
        Toggle hot reload on/off or check status
        Usage: !hotreload [on/off]
        """
        if enable is None:
            # Show current status
            status = "enabled" if hasattr(self, 'file_watcher') and self.file_watcher.is_running() else "disabled"
            embed = discord.Embed(
                title="🔥 Hot Reload Status",
                description=f"Hot reload is currently **{status}**",
                color=discord.Color.green() if status == "enabled" else discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        enable = enable.lower()
        if enable in ['on', 'true', 'enable', '1']:
            if not hasattr(self, 'file_watcher') or not self.file_watcher.is_running():
                if hasattr(self, 'file_watcher'):
                    self.file_watcher.restart()
                else:
                    self.file_watcher.start()
                embed = discord.Embed(
                    title="🔥 Hot Reload Enabled",
                    description="File watcher started - cogs will auto-reload on file changes",
                    color=discord.Color.green()
                )
                logger.info("Hot reload enabled via command")
            else:
                embed = discord.Embed(
                    title="🔥 Hot Reload",
                    description="Hot reload is already enabled",
                    color=discord.Color.orange()
                )
        elif enable in ['off', 'false', 'disable', '0']:
            if hasattr(self, 'file_watcher') and self.file_watcher.is_running():
                self.file_watcher.cancel()
                embed = discord.Embed(
                    title="🔥 Hot Reload Disabled",
                    description="File watcher stopped - use `!reload` for manual reloading",
                    color=discord.Color.red()
                )
                logger.info("Hot reload disabled via command")
            else:
                embed = discord.Embed(
                    title="🔥 Hot Reload",
                    description="Hot reload is already disabled",  
                    color=discord.Color.orange()
                )
        else:
            embed = discord.Embed(
                title="❌ Invalid Option",
                description="Use `on` or `off` to toggle hot reload",
                color=discord.Color.red()
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Development(bot))
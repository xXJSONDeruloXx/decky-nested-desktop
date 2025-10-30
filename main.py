import os
import subprocess
import base64
from pathlib import Path

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code repo
# and add the `decky-loader/plugin/imports` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky
import asyncio

class Plugin:
    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        self.loop = asyncio.get_event_loop()
        decky.logger.info("Hello World!")

    # Function called first during the unload process, utilize this to handle your plugin being stopped, but not
    # completely removed
    async def _unload(self):
        decky.logger.info("Goodnight World!")
        pass

    # Function called after `_unload` during uninstall, utilize this to clean up processes and other remnants of your
    # plugin that may remain on the system
    async def _uninstall(self):
        decky.logger.info("Goodbye World!")
        pass

    async def get_nested_desktop_shortcut_id(self) -> int:
        """Get or create a Steam shortcut for the nested desktop"""
        try:
            # Path to store the shortcut ID
            shortcut_id_file = Path(decky.DECKY_PLUGIN_SETTINGS_DIR) / "nested_desktop_shortcut_id.txt"
            
            # Try to read existing shortcut ID
            if shortcut_id_file.exists():
                try:
                    stored_id = int(shortcut_id_file.read_text().strip())
                    # Verify the shortcut still exists by trying to get its info
                    # The frontend will verify this with appStore
                    return stored_id
                except (ValueError, IOError):
                    pass
            
            # If we get here, we need to create a new shortcut
            # We'll return -1 to signal the frontend should create it
            # The frontend has access to SteamClient.Apps.AddShortcut
            return -1
            
        except Exception as e:
            decky.logger.error(f"Error managing shortcut ID: {str(e)}")
            return -1
    
    async def save_nested_desktop_shortcut_id(self, shortcut_id: int):
        """Save the shortcut ID for future use"""
        try:
            shortcut_id_file = Path(decky.DECKY_PLUGIN_SETTINGS_DIR) / "nested_desktop_shortcut_id.txt"
            shortcut_id_file.write_text(str(shortcut_id))
            decky.logger.info(f"Saved shortcut ID: {shortcut_id}")
            return True
        except Exception as e:
            decky.logger.error(f"Error saving shortcut ID: {str(e)}")
            return False

    async def create_nested_desktop_shortcut(self) -> dict:
        """Create a Steam shortcut for the steamos-nested-desktop file"""
        try:
            desktop_file = "/usr/share/applications/steam/steamos-nested-desktop/steamos-nested-desktop.desktop"
            
            if not os.path.exists(desktop_file):
                return {"success": False, "message": f"Desktop file not found at {desktop_file}"}
            
            # Return info needed for the frontend to create the shortcut
            return {
                "success": True,
                "desktop_file": desktop_file,
                "name": "Nested Desktop",
                "message": "Ready to create shortcut"
            }
        except Exception as e:
            decky.logger.error(f"Error preparing nested desktop shortcut: {str(e)}")
            return {"success": False, "message": f"Exception: {str(e)}"}
    
    async def get_nested_desktop_artwork(self) -> dict:
        """Get the artwork for nested desktop as base64 encoded strings"""
        try:
            # Files from defaults/ are copied to the plugin root directory during build
            plugin_dir = Path(decky.DECKY_PLUGIN_DIR)
            artwork = {}
            
            # Map artwork types to filenames
            artwork_files = {
                "grid": "grid.jpg",      # Vertical cover (600x900 recommended)
                "hero": "hero.jpg",      # Wide banner (1920x620 recommended)
                "logo": "logo.png",      # Transparent logo overlay
                "gridH": "gridH.jpg"     # Horizontal grid (920x430 recommended)
            }
            
            for art_type, filename in artwork_files.items():
                art_path = plugin_dir / filename
                if art_path.exists():
                    try:
                        with open(art_path, "rb") as f:
                            img_data = f.read()
                            # Encode to base64
                            b64_data = base64.b64encode(img_data).decode('ascii')
                            artwork[art_type] = b64_data
                            decky.logger.info(f"Loaded {art_type} artwork: {filename}")
                    except Exception as e:
                        decky.logger.error(f"Error loading {art_type} artwork: {str(e)}")
                        artwork[art_type] = None
                else:
                    decky.logger.warning(f"Artwork file not found: {art_path}")
                    artwork[art_type] = None
            
            return {"success": True, "artwork": artwork}
        except Exception as e:
            decky.logger.error(f"Error getting artwork: {str(e)}")
            return {"success": False, "message": f"Exception: {str(e)}", "artwork": {}}
    
    async def launch_nested_desktop_shortcut(self) -> dict:
        """Get the shortcut ID for launching - actual launch happens in frontend via SteamClient"""
        try:
            desktop_file = "/usr/share/applications/steam/steamos-nested-desktop/steamos-nested-desktop.desktop"
            
            if not os.path.exists(desktop_file):
                return {"success": False, "message": f"Desktop file not found at {desktop_file}"}
            
            # Path to store the shortcut ID
            shortcut_id_file = Path(decky.DECKY_PLUGIN_SETTINGS_DIR) / "nested_desktop_shortcut_id.txt"
            
            # Try to read existing shortcut ID
            if shortcut_id_file.exists():
                try:
                    stored_id = int(shortcut_id_file.read_text().strip())
                    decky.logger.info(f"Found existing shortcut ID: {stored_id}")
                    return {"success": True, "shortcut_id": stored_id, "message": "Ready to launch"}
                except (ValueError, IOError) as e:
                    decky.logger.error(f"Error reading shortcut ID: {str(e)}")
            
            # No valid shortcut ID found
            return {"success": False, "message": "No shortcut found. Please create one first."}
                
        except Exception as e:
            decky.logger.error(f"Exception getting shortcut ID: {str(e)}")
            return {"success": False, "message": f"Exception: {str(e)}"}
    
    async def save_nested_desktop_shortcut_id(self, shortcut_id: int) -> bool:
        """Save the shortcut ID for future use"""
        try:
            shortcut_id_file = Path(decky.DECKY_PLUGIN_SETTINGS_DIR) / "nested_desktop_shortcut_id.txt"
            shortcut_id_file.write_text(str(shortcut_id))
            decky.logger.info(f"Saved nested desktop shortcut ID: {shortcut_id}")
            return True
        except Exception as e:
            decky.logger.error(f"Error saving shortcut ID: {str(e)}")
            return False
    # Migrations that should be performed before entering `_main()`.
    async def _migration(self):
        decky.logger.info("Migrating")
        # Here's a migration example for logs:
        # - `~/.config/decky-template/template.log` will be migrated to `decky.decky_LOG_DIR/template.log`
        decky.migrate_logs(os.path.join(decky.DECKY_USER_HOME,
                                               ".config", "decky-template", "template.log"))
        # Here's a migration example for settings:
        # - `~/homebrew/settings/template.json` is migrated to `decky.decky_SETTINGS_DIR/template.json`
        # - `~/.config/decky-template/` all files and directories under this root are migrated to `decky.decky_SETTINGS_DIR/`
        decky.migrate_settings(
            os.path.join(decky.DECKY_HOME, "settings", "template.json"),
            os.path.join(decky.DECKY_USER_HOME, ".config", "decky-template"))
        # Here's a migration example for runtime data:
        # - `~/homebrew/template/` all files and directories under this root are migrated to `decky.decky_RUNTIME_DIR/`
        # - `~/.local/share/decky-template/` all files and directories under this root are migrated to `decky.decky_RUNTIME_DIR/`
        decky.migrate_runtime(
            os.path.join(decky.DECKY_HOME, "template"),
            os.path.join(decky.DECKY_USER_HOME, ".local", "share", "decky-template"))

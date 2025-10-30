import os
import base64
from pathlib import Path

import decky
import asyncio

class Plugin:
    async def _main(self):
        decky.logger.info("Nested Desktop plugin loaded")

    async def _unload(self):
        decky.logger.info("Nested Desktop plugin unloaded")

    async def _uninstall(self):
        decky.logger.info("Nested Desktop plugin uninstalled")

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

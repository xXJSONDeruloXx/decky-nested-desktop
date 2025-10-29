import os
import pwd
from pathlib import Path

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code repo
# and add the `decky-loader/plugin/imports` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky
import asyncio

class Plugin:
    # A normal method. It can be called from the TypeScript side using @decky/api.
    async def add(self, left: int, right: int) -> int:
        return left + right

    async def long_running(self):
        await asyncio.sleep(15)
        # Passing through a bunch of random data, just as an example
        await decky.emit("timer_event", "Hello from the backend!", True, 2)

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

    async def start_timer(self):
        self.loop.create_task(self.long_running())

    async def start_plasma_wayland(self):
        """Execute the Plasma Wayland script"""
        try:
            decky.logger.info("Starting Plasma Wayland session...")
            
            # Create a clean environment but preserve session-critical variables
            # Start with a copy and remove only the problematic library variables
            clean_env = os.environ.copy()
            clean_env.pop('LD_PRELOAD', None)
            clean_env.pop('LD_LIBRARY_PATH', None)
            
            # Ensure UTF-8 locale
            clean_env.setdefault('LC_ALL', 'C.UTF-8')
            clean_env.setdefault('LANG', 'C.UTF-8')

            # Derive the Deck user details even when the plugin runs as root
            deck_user = getattr(decky, "DECKY_USER", None)
            deck_home = getattr(decky, "DECKY_USER_HOME", None)
            if not deck_user and deck_home:
                deck_user = Path(deck_home).name
            if not deck_user:
                raise RuntimeError("Unable to determine Deck user from decky environment")

            try:
                deck_uid = pwd.getpwnam(deck_user).pw_uid
            except KeyError as exc:
                raise RuntimeError(f"Unable to resolve uid for user '{deck_user}'") from exc

            runtime_dir = Path(f"/run/user/{deck_uid}")
            if not runtime_dir.is_dir():
                raise RuntimeError(
                    f"XDG_RUNTIME_DIR missing at {runtime_dir}; ensure Deck user session is active"
                )

            bus_path = runtime_dir / 'bus'
            if not bus_path.exists():
                raise RuntimeError(
                    f"DBUS session bus not found at {bus_path}; ensure Deck user session is active"
                )

            clean_env['XDG_RUNTIME_DIR'] = str(runtime_dir)
            clean_env['DBUS_SESSION_BUS_ADDRESS'] = f"unix:path={bus_path}"
            clean_env['USER'] = deck_user
            clean_env['LOGNAME'] = deck_user
            
            # Get DISPLAY value
            display = clean_env.get('DISPLAY', ':0')
            
            # Use systemd-run to start it as a proper user service
            # This gives it a clean session context
            command = [
                'sudo',
                '-E',
                '-u', deck_user,
                'systemd-run',
                '--user',
                '--scope',
                '--collect',
                'startplasma-wayland',
                '--xwayland',
                '--x11-display', display,
                '--no-lockscreen',
                '--width', '1280',
                '--height', '800',
                '--',
                'plasma_session'
            ]
            
            # Execute the command with cleaned environment
            process = await asyncio.create_subprocess_exec(
                *command,
                env=clean_env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            stdout_text = stdout.decode().strip() if stdout else ""
            stderr_text = stderr.decode().strip() if stderr else ""

            if process.returncode == 0:
                if stdout_text:
                    decky.logger.info(f"Plasma Wayland launch scheduled: {stdout_text}")
                else:
                    decky.logger.info("Plasma Wayland launch scheduled")
                return {
                    "success": True,
                    "message": stdout_text or "Plasma Wayland start requested successfully"
                }

            error_msg = stderr_text or stdout_text or "systemd-run exited with non-zero status"
            decky.logger.error(f"Failed to start Plasma Wayland: {error_msg}")
            return {"success": False, "message": f"Error: {error_msg}"}
        except Exception as e:
            decky.logger.error(f"Exception starting Plasma Wayland: {str(e)}")
            return {"success": False, "message": f"Exception: {str(e)}"}

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

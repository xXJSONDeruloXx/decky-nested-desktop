#!/bin/sh

# Nested Desktop Mode launcher for Steam Deck
# Based on the original nested desktop shortcut

# Unset Steam's library preload to avoid conflicts
unset LD_PRELOAD

# Clean up and create temporary directory for the wrapper
rm -rf /tmp/desktop-mode
mkdir -p /tmp/desktop-mode

# Create a wrapper script for kwin_wayland_wrapper with custom settings
cat > /tmp/desktop-mode/kwin_wayland_wrapper << EOF
#!/bin/sh
$(which kwin_wayland_wrapper) --no-lockscreen --width 1280 --height 800 --x11-display \$DISPLAY \$@
EOF

chmod +x /tmp/desktop-mode/kwin_wayland_wrapper

# Disable systemd boot for KDE startup to avoid session conflicts
kwriteconfig5 --file startkderc --group General --key systemdBoot false

# Launch Plasma Wayland with our custom wrapper in PATH
PATH=/tmp/desktop-mode:$PATH startplasma-wayland

# Restore systemd boot setting
kwriteconfig5 --file startkderc --group General --key systemdBoot --delete


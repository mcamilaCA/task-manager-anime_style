#!/bin/bash
# Builds/refreshes a double-clickable "Apothecary's Almanac.app" on the
# Desktop that launches this project without needing a terminal.
set -euo pipefail

APP_NAME="Apothecary's Almanac"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$HOME/Desktop/$APP_NAME.app"

rm -rf "$DEST"
mkdir -p "$DEST/Contents/MacOS" "$DEST/Contents/Resources"

cp "$REPO_DIR/app/assets/icon/AppIcon.icns" "$DEST/Contents/Resources/AppIcon.icns"

cat > "$DEST/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleDisplayName</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.local.apothecarysalmanac</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleExecutable</key>
    <string>launch</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

cat > "$DEST/Contents/MacOS/launch" <<LAUNCH
#!/bin/bash
REPO_DIR="$REPO_DIR"
LOG_DIR="\$HOME/.apothecarys_almanac"
mkdir -p "\$LOG_DIR"

PYTHON_BIN="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"
cd "\$REPO_DIR" || exit 1

if [ -x "\$PYTHON_BIN" ]; then
    exec "\$PYTHON_BIN" main.py >> "\$LOG_DIR/launch.log" 2>&1
else
    exec /bin/zsh -l -c "cd '\$REPO_DIR' && python3 main.py" >> "\$LOG_DIR/launch.log" 2>&1
fi
LAUNCH

chmod +x "$DEST/Contents/MacOS/launch"

echo "Built: $DEST"

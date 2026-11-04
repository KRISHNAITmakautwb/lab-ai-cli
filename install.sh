#!/bin/bash
echo "🧠 Installing Lab AI CLI..."

# Ensure pip dependencies are installed quietly
if command -v pip3 &> /dev/null; then
    # Modern Linux distros (Ubuntu 23+, Debian 12+) block global pip installs.
    # We try normal install first, and if it fails due to PEP 668, we add the override flag.
    export PIP_ROOT_USER_ACTION=ignore
    pip3 install requests rich --quiet || pip3 install requests rich --quiet --break-system-packages
else
    echo "Error: Python3 pip is required to install this CLI."
    exit 1
fi

# Clean up any conflicting old local installations across user directories
for user_dir in /home/*; do
    if [ -f "$user_dir/.local/bin/cryptos" ]; then
        echo "🧹 Removing old local installation at $user_dir/.local/bin/cryptos"
        rm -f "$user_dir/.local/bin/cryptos"
    fi
done

# Download the script directly to the binaries folder
curl -s http://10.10.1.226:9000/lab-cli.py -o /usr/local/bin/cryptos
chmod +x /usr/local/bin/cryptos

echo "✅ Installation complete!"
echo "You can now launch the AI from anywhere by simply typing: cryptos"

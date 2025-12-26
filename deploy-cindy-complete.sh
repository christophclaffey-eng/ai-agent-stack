#!/bin/bash
set -e

echo "🚀 Deploying Complete Cindy System..."
cd ~/ai-agent-stack

# Backup
mkdir -p ~/ai-stack-backups/pre-cindy-$(date +%Y%m%d)
cp -r langchain-server ~/ai-stack-backups/pre-cindy-$(date +%Y%m%d)/ 2>/dev/null || true

# Download the main.py from artifact "Cindy - Complete AI Assistant System"
# Download the cindy.html from artifact "Cindy Tablet Interface"  
# Download docker-compose.yml with proper configuration

echo "Paste the Cindy main.py code (from artifact)"
echo "Press Ctrl+D when done"
cat > langchain-server/main.py

mkdir -p langchain-server/static

echo "Paste the Cindy tablet HTML (from artifact)"
echo "Press Ctrl+D when done"
cat > langchain-server/static/cindy.html

# Restart
docker-compose down
docker-compose up -d --build

sleep 20

echo "✅ Cindy deployed!"
echo "Open: http://localhost:8000"

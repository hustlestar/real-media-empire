#!/bin/bash
# Simple deployment script for pdf-link-youtube-to-anything-tg-bot

set -e

echo "🚀 Deploying pdf-link-youtube-to-anything-tg-bot..."

# Update code
echo "📦 Pulling latest changes..."
git pull origin main || git pull origin master

# Update dependencies
echo "📚 Installing dependencies..."
source venv/bin/activate || python3.11 -m venv venv && source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
echo "🗄️ Running database migrations..."
pdf-link-youtube-to-anything-tg-bot migrate || python -m cli migrate

# Restart service
echo "🔄 Restarting service..."
sudo systemctl restart pdf-link-youtube-to-anything-tg-bot.service

# Check status
echo "✅ Checking service status..."
sudo systemctl status pdf-link-youtube-to-anything-tg-bot.service --no-pager

echo "✨ Deployment complete!"
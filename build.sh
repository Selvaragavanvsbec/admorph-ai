#!/usr/bin/env bash
# Build script for Render deployment

set -e

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Installing Playwright Chromium ==="
playwright install chromium
playwright install-deps chromium || echo "WARN: install-deps requires root, skipping"

echo "=== Building Frontend ==="
cd frontend
npm install
npm run build
cd ..

echo "=== Creating required directories ==="
mkdir -p generated/audio
mkdir -p assets/processed
mkdir -p assets/uploads

echo "=== Build Complete ==="

# FactSticker Chrome Extension

Quiz yourself on any article you're reading!

## Installation

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select this `chrome-extension` folder

## Usage

1. Make sure the Flask server is running (`python app.py`)
2. Navigate to any article you want to be quizzed on
3. Click the FactSticker extension icon
4. A new tab opens with quiz questions about the article

## Icons

You need to add icon files:
- `icon16.png` (16x16 pixels)
- `icon48.png` (48x48 pixels)
- `icon128.png` (128x128 pixels)

You can create simple icons or use a placeholder. The extension will work without icons but will show a default puzzle piece.

## Configuration

Edit `background.js` to change the server URL if not running on localhost:5001.

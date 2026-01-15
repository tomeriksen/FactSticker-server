# FactSticker

A quiz application that generates multiple-choice questions from web articles using OpenAI.

## Architecture Overview

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────┐
│  Chrome Extension   │────>│   Flask Server      │────>│   OpenAI API    │
│  (content extract)  │     │   (app.py)          │     │   (gpt-4o-mini) │
└─────────────────────┘     └─────────────────────┘     └─────────────────┘
         │                           │
         │                           v
         │                  ┌─────────────────────┐
         └─────────────────>│   Quiz UI           │
                            │   (quiz.html)       │
                            └─────────────────────┘
```

## Components

### 1. Chrome Extension (`chrome-extension/`)

Extracts article content from the current browser tab and sends it to the server.

**Files:**
- `manifest.json` - Extension configuration (Manifest V3)
- `background.js` - Service worker that handles content extraction

**Flow:**
1. User clicks extension icon on any article page
2. Extension extracts DOM content (paragraphs, headings, list items)
3. Stores content in `chrome.storage.local`
4. Opens quiz page with `?ext=1` parameter
5. Quiz page requests content via `chrome.runtime.sendMessage`

**Permissions:**
- `activeTab` - Access current tab
- `scripting` - Execute content extraction script
- `storage` - Store extracted content

### 2. Flask Server (`app.py`)

Backend API that manages quiz sessions and communicates with OpenAI.

**Key Routes:**

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page with URL input form |
| `/quiz` | GET | Quiz UI page |
| `/api/quiz/start` | POST | Generate questions from article |
| `/api/quiz/next` | POST | Get next question in session |

**Quiz Flow:**
1. `/api/quiz/start` receives URL and optional content from extension
2. If no content provided, server scrapes article using `article_scraper.py`
3. Calls `generate_quiz_questions()` to get questions from OpenAI
4. Stores questions in Flask session
5. Returns first question with `total_questions` count

### 3. OpenAI Integration (`openai_response.py`)

Generates quiz questions from article content.

**Function:** `generate_quiz_questions(content, title, url, num_questions)`

**Returns:** List of question objects:
```json
{
  "question": "Question text?",
  "options": {"a": "Option A", "b": "Option B", "c": "Option C"},
  "correct": "b",
  "explanations": {
    "a": "Incorrect. Explanation...",
    "b": "Correct! Explanation...",
    "c": "Incorrect. Explanation..."
  }
}
```

**Model Settings:**
- Model: `gpt-4o-mini`
- Temperature: `0.3` (deterministic)
- Seed: `42` (reproducible results)

### 4. Quiz UI (`templates/quiz.html`)

Codecademy-style interactive quiz interface.

**Features:**
- Single question display with A/B/C options
- Instant feedback with explanations
- Progress indicator (Question X of Y)
- Score tracking
- "Harder Quiz" button on perfect score

**Communication with Extension:**
- Checks for `?ext=1` URL parameter
- Requests content via `chrome.runtime.sendMessage`
- Falls back to server-side scraping if no extension content

### 5. Article Scraper (`article_scraper.py`)

Server-side fallback for extracting article content when extension isn't used.

**Function:** `extract_article(url)`

Uses `readability-lxml` and `BeautifulSoup` to extract main article content.

## Setup

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation

```bash
# Clone repository
git clone <repo-url>
cd FactSticker-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the Server

```bash
python3 app.py
```

Server runs at `http://127.0.0.1:5001`

### Installing Chrome Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select the `chrome-extension/` folder

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `SECRET_KEY` | Flask session secret key |

## Data Flow

1. **User visits article** in Chrome
2. **Clicks extension** icon
3. **Extension extracts** article text from DOM
4. **Extension opens** quiz page with content stored locally
5. **Quiz page requests** content from extension
6. **Quiz page sends** content to `/api/quiz/start`
7. **Server calls** OpenAI to generate questions
8. **Server stores** questions in session, returns first question
9. **User answers** questions, gets instant feedback
10. **User clicks "Next"** to get subsequent questions from session

# Mindful Chat

A mental wellness companion web app. Chat with an emotion-aware bot, track your mood, set reminders, and access crisis resources.

## Features

- **Landing & About** — Public pages introducing the app
- **Login / Register** — Simple account creation
- **Chat** — Emotion-aware chatbot (detects stress, anxiety, sadness, happiness)
- **Mood Graph** — Visualize your mood trend over time
- **Export** — Download chat history as PDF
- **Profile** — Bio and preferences
- **Reminders** — Daily check-in reminders
- **Resources** — Crisis helplines and self-care tips

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS (responsive)
- **Charts:** Matplotlib
- **PDF:** ReportLab

## Project Structure

```
mental_health_web_full/
├── src/
│   ├── __init__.py
│   └── app.py          # Flask app and routes
├── templates/          # HTML templates
├── static/             # CSS and static assets
├── run.py              # Entry point
├── requirements.txt
├── Procfile            # For deployment
├── render.yaml         # Render.com config
└── deploy/
    └── DEPLOY.md       # Deployment guide
```

## Setup

1. **Clone the repo** (or navigate to the project folder).

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate it:**
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the app:**
   ```bash
   python run.py
   ```

6. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Deployment

See [deploy/DEPLOY.md](deploy/DEPLOY.md) for deploying to Render, Railway, or PythonAnywhere.

## License

MIT

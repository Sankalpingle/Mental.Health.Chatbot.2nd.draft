# Deploy Mindful Chat to the Web

## Option 1: Render (Recommended — Free)

1. **Push your code to GitHub**  
   Create a repo and push this project.

2. **Sign up at [render.com](https://render.com)** (free account).

3. **Create a new Web Service**
   - Dashboard → New → Web Service
   - Connect your GitHub repo
   - Render will detect the `render.yaml` config at project root

4. **Or configure manually**
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn src.app:app`
   - Add env var: `SECRET_KEY` = (generate a random string)

5. **Deploy** — Render builds and deploys automatically. You get a URL like `https://mindful-chat-xxx.onrender.com`.

**Note:** On Render's free tier, the SQLite database resets when the app restarts. For persistent data, use a PostgreSQL database (Render offers a free add-on).

---

## Option 2: PythonAnywhere

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your project or clone from GitHub
3. Create a virtualenv and install: `pip install -r requirements.txt`
4. Add a new web app (Flask)
5. Point it to your app: `app = app` in the Flask app config
6. Set `SECRET_KEY` in the web app config

---

## Option 3: Railway

1. Sign up at [railway.app](https://railway.app)
2. New Project → Deploy from GitHub
3. The `Procfile` at project root: `web: gunicorn src.app:app`
4. Railway auto-detects Python and deploys

---

## Before Going Live

- [ ] Set a strong `SECRET_KEY` in your hosting dashboard (never commit it)
- [ ] Use HTTPS (Render, Railway, PythonAnywhere provide it)
- [ ] For production, consider PostgreSQL for persistent data

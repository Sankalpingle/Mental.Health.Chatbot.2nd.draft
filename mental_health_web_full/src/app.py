from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer  # type: ignore
from reportlab.lib.styles import getSampleStyleSheet  # type: ignore
from reportlab.lib.units import inch  # type: ignore

# Project root (parent of src/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey-dev-only")

# ---------------- DATABASE ----------------
conn = sqlite3.connect(
    os.path.join(BASE_DIR, "chatbot_full.db"), check_same_thread=False
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats(
    username TEXT,
    timestamp TEXT,
    message TEXT,
    emotion TEXT,
    response TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS profiles(
    username TEXT PRIMARY KEY,
    bio TEXT,
    preferences TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    reminder_time TEXT,
    note TEXT
)
""")

try:
    cursor.execute("ALTER TABLE chats ADD COLUMN response TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass

# ---------------- EMOTION LOGIC ----------------
emotion_keywords = {
    "stress": ["stress", "pressure", "overwhelmed", "exam"],
    "anxiety": ["anxious", "panic", "worried", "fear"],
    "sadness": ["sad", "lonely", "depressed", "unhappy"],
    "happy": ["happy", "good", "great", "fine"]
}

emergency_keywords = ["suicide", "kill myself", "die"]

emotion_score = {
    "happy": 4,
    "neutral": 3,
    "stress": 2,
    "anxiety": 1,
    "sadness": 1,
    "emergency": 0
}


def detect_emotion(text):
    text = text.lower()
    for word in emergency_keywords:
        if word in text:
            return "emergency"
    for emotion, words in emotion_keywords.items():
        for word in words:
            if word in text:
                return emotion
    return "neutral"


def generate_response(emotion):
    responses = {
        "stress": "You seem stressed. Try deep breathing 🌿",
        "anxiety": "Take slow breaths and stay present.",
        "sadness": "I'm sorry you're feeling this way 💛",
        "happy": "That's wonderful to hear! 😊",
        "neutral": "Tell me more about how you're feeling.",
        "emergency": "⚠ If you're feeling unsafe, contact a trusted person or professional immediately."
    }
    return responses.get(emotion)


# ---------------- ROUTES ----------------

@app.route("/")
def landing():
    if session.get("user"):
        return redirect("/dashboard")
    return render_template("landing.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/resources")
def resources():
    return render_template("resources.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user"):
        return redirect("/dashboard")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                       (username, password))
        if cursor.fetchone():
            session["user"] = username
            return redirect("/dashboard")
        cursor.execute("INSERT OR IGNORE INTO users VALUES (?, ?)",
                       (username, password))
        conn.commit()
        session["user"] = username
        return redirect("/dashboard")
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html", user=session["user"])


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "user" not in session:
        return redirect("/login")
    username = session["user"]

    if request.method == "POST":
        message = request.form["message"]
        emotion = detect_emotion(message)
        response = generate_response(emotion)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO chats VALUES (?, ?, ?, ?, ?)",
                       (username, timestamp, message, emotion, response))
        conn.commit()

    cursor.execute("SELECT timestamp, message, emotion, response FROM chats WHERE username=?",
                   (username,))
    chats = cursor.fetchall()
    return render_template("chat.html", user=username, chats=chats)


@app.route("/graph")
def graph():
    if "user" not in session:
        return redirect("/login")
    username = session["user"]
    cursor.execute("SELECT emotion FROM chats WHERE username=?", (username,))
    data = cursor.fetchall()

    if not data:
        return "No data available"

    scores = [emotion_score.get(row[0], 3) for row in data]
    plt.figure()
    plt.plot(scores)
    plt.title("Mood Trend")
    plt.xlabel("Session")
    plt.ylabel("Mood Score")

    static_dir = os.path.join(BASE_DIR, "static")
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    path = os.path.join(static_dir, "mood_graph.png")
    plt.savefig(path)
    plt.close()
    return send_file(path, mimetype="image/png")


@app.route("/export")
def export_pdf():
    if "user" not in session:
        return redirect("/login")
    username = session["user"]
    cursor.execute("SELECT timestamp, message, emotion, response FROM chats WHERE username=?",
                   (username,))
    records = cursor.fetchall()

    file_name = os.path.join(BASE_DIR, "chat_report.pdf")
    doc = SimpleDocTemplate(file_name)
    elements = []
    styles = getSampleStyleSheet()
    for r in records:
        text = f"{r[0]} | {r[1]} | Emotion: {r[2]}" + (f" | Response: {r[3]}" if r[3] else "")
        elements.append(Paragraph(text, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))
    doc.build(elements)
    return send_file(file_name, as_attachment=True)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect("/login")
    username = session["user"]
    if request.method == "POST":
        bio = request.form.get("bio", "")
        preferences = request.form.get("preferences", "")
        cursor.execute("""
            INSERT OR REPLACE INTO profiles (username, bio, preferences) VALUES (?, ?, ?)
        """, (username, bio, preferences))
        conn.commit()
        return redirect("/profile")
    cursor.execute("SELECT bio, preferences FROM profiles WHERE username=?", (username,))
    row = cursor.fetchone()
    profile_data = {"bio": row[0] if row else "", "preferences": row[1] if row else ""}
    return render_template("profile.html", profile=profile_data)


@app.route("/reminders", methods=["GET", "POST"])
def reminders():
    if "user" not in session:
        return redirect("/login")
    username = session["user"]
    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "add":
            reminder_time = request.form.get("reminder_time", "")
            note = request.form.get("reminder_note", "")
            if reminder_time:
                cursor.execute(
                    "INSERT INTO reminders (username, reminder_time, note) VALUES (?, ?, ?)",
                    (username, reminder_time, note)
                )
                conn.commit()
        elif action == "delete":
            rid = request.form.get("reminder_id")
            if rid:
                cursor.execute("DELETE FROM reminders WHERE id=? AND username=?", (rid, username))
                conn.commit()
        return redirect("/reminders")
    cursor.execute("SELECT id, reminder_time, note FROM reminders WHERE username=? ORDER BY reminder_time",
                   (username,))
    reminders_list = cursor.fetchall()
    return render_template("reminders.html", reminders=reminders_list)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

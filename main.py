from fastapi import FastAPI, Request
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import requests
import datetime

# --- WhatsApp API Config ---
TOKEN = "EAAfhBHu2xBIBPaNUnKBhG5KKLO9u1KVPkZAzzPZA7AdbCAoLqIC7LZA9cZAut6MdIuefhtGsxIvSaIu0e7jnG4jYZCv5SFygxXnlAtzqMd86X9P2cPUiw3F38pvpuIyUG4gwyPPEAwsqDtJTR8s732NYNHwBX0Bu7XrQWTarp1z7Ds7Vbh3IwYXZAZBRHY1YFKF2wZDZD"
PHONE_NUMBER_ID = "803051552882522"
API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

# --- Database Setup ---
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_number TEXT,
    meter_name TEXT,
    days INTEGER,
    next_reminder TEXT
)
""")
conn.commit()

# --- FastAPI App ---
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Meter Reminder App is Running ✅"}

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    try:
        user_number = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        user_text = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

        # Example message: "Shop 15"
        parts = user_text.split()
        meter_name = parts[0]
        days = int(parts[1])

        next_reminder = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")

        cursor.execute("INSERT INTO reminders (user_number, meter_name, days, next_reminder) VALUES (?, ?, ?, ?)",
                       (user_number, meter_name, days, next_reminder))
        conn.commit()

        send_message(user_number, f"✅ Reminder set for {meter_name} after {days} days ({next_reminder}).")

    except Exception as e:
        print("Error:", e)
    return {"status": "ok"}

# --- WhatsApp Send Function ---
def send_message(to, message):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    requests.post(API_URL, headers=headers, json=payload)

# --- Scheduler Job ---
def check_reminders():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT id, user_number, meter_name, days FROM reminders WHERE next_reminder=?", (today,))
    reminders = cursor.fetchall()

    for r in reminders:
        reminder_id, user_number, meter_name, days = r
        send_message(user_number, f"⏰ Reminder: Please check {meter_name} meter today!")

        # reset next reminder
        next_reminder = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        cursor.execute("UPDATE reminders SET next_reminder=? WHERE id=?", (next_reminder, reminder_id))
        conn.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(check_reminders, "interval", minutes=1)
scheduler.start()

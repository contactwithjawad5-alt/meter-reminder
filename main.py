from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔑 Meta / WhatsApp credentials (sab Render Environment Variables se aayenge)
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mysecrettokenreminder")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

@app.route("/", methods=["GET"])
def home():
    return "✅ WhatsApp Reminder Bot is running!", 200


# ✅ Webhook route
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verification ke liye
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification token mismatch", 403

    if request.method == "POST":
        data = request.get_json()
        print("📩 Webhook event received:", data)

        # Agar message aaya hai to auto reply bhejo
        if "entry" in data:
            for entry in data["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if "value" in change and "messages" in change["value"]:
                            for message in change["value"]["messages"]:
                                sender = message["from"]  # user ka number
                                text = message.get("text", {}).get("body", "")

                                if text:
                                    send_whatsapp_message(sender, f"✅ Received your message: {text}")

        return "EVENT_RECEIVED", 200


# ✅ Send WhatsApp message function
def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    response = requests.post(url, headers=headers, json=payload)
    print("📤 Send message response:", response.json())
    return response.json()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

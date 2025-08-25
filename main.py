from fastapi import FastAPI, Request
import requests

app = FastAPI()

# === WhatsApp API Config ===
ACCESS_TOKEN = "EAAfhBHu2xBIBPaNUnKBhG5KKLO9u1KVPkZAzzPZA7AdbCAoLqIC7LZA9cZAut6MdIuefhtGsxIvSaIu0e7jnG4jYZCv5SFygxXnlAtzqMd86X9P2cPUiw3F38pvpuIyUG4gwyPPEAwsqDtJTR8s732NYNHwBX0Bu7XrQWTarp1z7Ds7Vbh3IwYXZAZBRHY1YFKF2wZDZD"
PHONE_NUMBER_ID = "803051552882522"
VERIFY_TOKEN = "mysecrettokenreminder"  # 👈 ye apna khud ka token rakho

# === Send WhatsApp Message ===
def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# === Webhook Verify (Meta check karega) ===
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return int(params["hub.challenge"])
    return {"error": "Verification failed"}

# === Webhook Receive (jab user msg bhejta hai) ===
@app.post("/webhook")
async def receive_webhook(request: Request):
    data = await request.json()
    print("Webhook Data:", data)

    # Agar user ne text bheja
    try:
        phone_number = data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        message_text = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

        print(f"User: {phone_number} | Message: {message_text}")

        # Auto reply bhejna
        reply = f"📩 Aapne yeh message bheja: {message_text}"
        send_whatsapp_message(phone_number, reply)

    except Exception as e:
        print("Error parsing message:", e)

    return {"status": "ok"}

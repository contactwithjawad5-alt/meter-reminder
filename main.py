from fastapi import FastAPI
import requests

app = FastAPI()

ACCESS_TOKEN = "EAAfhBHu2xBIBPaNUnKBhG5KKLO9u1KVPkZAzzPZA7AdbCAoLqIC7LZA9cZAut6MdIuefhtGsxIvSaIu0e7jnG4jYZCv5SFygxXnlAtzqMd86X9P2cPUiw3F38pvpuIyUG4gwyPPEAwsqDtJTR8s732NYNHwBX0Bu7XrQWTarp1z7Ds7Vbh3IwYXZAZBRHY1YFKF2wZDZD"
PHONE_NUMBER_ID = "803051552882522"

def send_whatsapp_message(to_number: str, message: str):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@app.get("/send/{number}")
def send_message(number: str, msg: str = "Hello! This is your meter reminder 🚀"):
    return send_whatsapp_message(number, msg)

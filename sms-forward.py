
from dotenv import load_dotenv
import json
import os
import pytz
import requests
import subprocess
import time

load_dotenv(dotenv_path=os.path.expanduser(".env"))

# Configuration
SMS_WEBHOOK_URL = os.getenv("SMS_WEBHOOK_URL", "https://endpoint.request")
SMS_SENDER = os.getenv("SMS_SENDER", "8675309")
TIMEZONE = "America/New_York"  # EST timezone
REMOVE_PHRASES = ["DO NO TRADE", "NTO A RECO", "Reply STOP to Quit", "NOT A RECO DO NOT TRADE"]

last_sms_cache = None

def clean_message(message):
    """Removes unwanted phrases from the message."""
    for phrase in REMOVE_PHRASES:
        message = message.replace(phrase, "")  # Replace only the first occurrence
    return message.strip()  # Remove extra spaces if needed


def is_within_schedule():
    """Check if the current time is between 6 AM - 9 PM EST (Monday-Friday)."""
    est = pytz.timezone(TIMEZONE)
    now = datetime.now(est)
    return now.weekday() < 5 and 6 <= now.hour < 21  # Monday to Friday, 6 AM - 9 PM

def get_latest_sms():
    """Fetch the latest SMS using termux-sms-list."""
    try:
        output = subprocess.check_output(["termux-sms-list", "-l", "1"]).decode("utf-8")
        sms_list = json.loads(output)
        if sms_list:
            return sms_list[0]  # Return the most recent message
    except Exception as e:
        print(f"Error fetching SMS: {e}")
    return None

def send_sms_to_webhook(sms):
    """Send SMS data to a webhook."""
    message_text = clean_message(sms["body"])
    payload = {
        "content": f"📩 **New SMS Received**\n**From:** {sms['number']}\n**Message:** {message_text}"
    }
    
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(SMS_WEBHOOK_URL, json=payload, headers=headers)
        if response.status_code == 200 or response.status_code == 204:
            print(f"✅ Sent to: {sms}")
        else:
            print(f"❌ Failed to send: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending SMS: {e}")

def send_sms_to_webhook_old(sms):
    """Send the SMS data to a webhook."""
    payload = {
        "from": sms["number"],
        "message": sms["body"],
        "timestamp": sms["received"]
    }
    print(payload)
    try:
        response = requests.post(SMS_WEBHOOK_URL, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print(f"✅ Sent to webhook: {sms}")
        else:
            print(f"❌ Failed to send: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending SMS: {e}")

def main():
    """Main loop that runs continuously but executes only during market hours."""
    global last_sms_cache  # Use an in-memory cache instead of a file

    while True:
        if is_within_schedule():
            sms = get_latest_sms()
            if sms and sms["number"] == SMS_SENDER:
                if last_sms_cache is None or sms["body"] != last_sms_cache["body"]:
                    send_sms_to_webhook(sms)
                    last_sms_cache = sms  # Store in memory to prevent duplicates

            time.sleep(5)  # Check every 5 seconds
        else:
            print("⏸️ Outside of schedule, sleeping...")
            time.sleep(60 * 15)  # Sleep for 15 minutes before checking again

if __name__ == "__main__":
    main()

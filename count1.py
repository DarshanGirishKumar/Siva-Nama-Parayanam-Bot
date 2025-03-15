import requests
import re
import datetime
import schedule
import time
import json

# 🔹 Replace with your Ultramsg API details
ULTRAMSG_INSTANCE_ID = "instance110229"
ULTRAMSG_TOKEN = "k2cfk51fp28tuup8"
GROUP_ID = "120363393806699556@g.us"  # Your WhatsApp Group ID

# File to store overall total count
TOTAL_COUNT_FILE = "total_count.json"

def load_total_count():
    """Load the stored overall total count from the file."""
    try:
        with open(TOTAL_COUNT_FILE, "r") as f:
            data = json.load(f)
        return data.get("total", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0  # If file doesn't exist, start with 0

def save_total_count(new_total):
    """Save the updated overall total count to the file."""
    with open(TOTAL_COUNT_FILE, "w") as f:
        json.dump({"total": new_total}, f)

def get_latest_siva_nama_message():
    """Fetch the latest message containing 'Siva Nama Parayanam'."""
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/chats/messages"
    params = {
        "token": ULTRAMSG_TOKEN,
        "chatId": GROUP_ID,
        "limit": 10  # Fetch last 10 messages to find the latest relevant one
    }

    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"❌ API Error: {response.text}")
        return None

    messages = response.json()
    
    if not messages:
        print("⚠️ No messages found in the group.")
        return None

    # Get today's date
    today_date = datetime.datetime.today().strftime("%d.%m.%Y")
    
    # Find the last message that contains 'Siva Nama Parayanam' and is from today
    for message in messages:
        if "siva nama parayanam" in message["body"].lower() and today_date in message["body"]:
            print(f"\n✅ Found 'Siva Nama Parayanam' Message:\n{message['body']}\n")
            return message["body"]

    print(f"⚠️ No valid 'Siva Nama Parayanam' message found for today ({today_date}).")
    return None


def extract_count_from_message(message):
    """Extract and sum up the counts from the latest message."""
    lines = message.split("\n")[1:]  # Skip the first line (title & date)
    numbers = [int(re.search(r"\d+$", line).group()) for line in lines if re.search(r"\d+$", line)]

    return sum(numbers)

def send_whatsapp_message(message):
    """Send a message via WhatsApp using Ultramsg API."""
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": GROUP_ID,
        "body": message
    }

    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print(f"✅ Message sent: {message}")
    else:
        print(f"❌ Error sending message: {response.text}")

def send_night_summary():
    """Fetch the latest 'Siva Nama Parayanam' message, calculate total count, and send a summary message."""
    last_message = get_latest_siva_nama_message()
    if not last_message:
        print("⚠️ No valid 'Siva Nama Parayanam' message found. Skipping summary.")
        return

    # Extract count from the last message
    daily_total = extract_count_from_message(last_message)
    
    # Update the total count
    overall_total = load_total_count() + daily_total
    save_total_count(overall_total)

    today = datetime.datetime.today().strftime("%d.%m.%Y %A")
    summary_message = f"{today}'s count\n{daily_total}\nTotal {overall_total}"

    send_whatsapp_message(summary_message)

# Schedule the script to run every day at a specific time
schedule.every().day.at("12:57").do(send_night_summary)  # Adjust time as needed

# Keep the script running
print("🚀 Night Summary Bot Running...")
while True:
    schedule.run_pending()
    time.sleep(10)

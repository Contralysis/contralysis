from dotenv import load_dotenv, find_dotenv
import os

dotenv_path = find_dotenv()
if not dotenv_path:
    print("Could not find .env file.")
else:
    print(f"Found .env file at: {dotenv_path}")

load_success = load_dotenv()
if load_success:
    print(".env file loaded successfully.")
else:
    print("Failed to load .env file.")

class Config:
    FIREBASE_CONFIG = {
        "apiKey": os.getenv('FIREBASE_API_KEY'),
        "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN'),
        "projectId": os.getenv('FIREBASE_PROJECT_ID'),
        "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET'),
        "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        "appId": os.getenv('FIREBASE_APP_ID'),
    }

# Print out the loaded environment variables for debugging
print("Loaded Firebase Config:")
for key, value in Config.FIREBASE_CONFIG.items():
    print(f"{key}: {value}")
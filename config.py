from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Fetch the API token
API_TOKEN = os.getenv("API_TOKEN")


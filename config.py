import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch API token from environment variables
API_TOKEN = os.getenv("API_TOKEN")

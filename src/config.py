import os
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.getenv("NEOSTATS_ENDPOINT", "https://neo-hackathon.services.ai.azure.com/openai/v1/")
API_KEY = os.getenv("NEOSTATS_API_KEY", "")
MODEL_NAME = os.getenv("NEOSTATS_MODEL", "Neo-Hackathon")

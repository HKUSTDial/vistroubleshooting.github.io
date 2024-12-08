"""Configuration settings for the project."""
import os
from dotenv import load_dotenv


load_dotenv()


API_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "base_url": os.getenv("OPENAI_BASE_URL")
}


PATH_CONFIG = {
    "input_dir": "dataset",
    "output_dir": "output"
} 
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """
    Application configuration loaded from environment variables or defaults.
    """
    def __init__(self):
        # Database settings
        self.DB_HOST = os.getenv("DB_HOST", "localhost")
        self.DB_PORT = int(os.getenv("DB_PORT", 3306))
        self.DB_USER = os.getenv("DB_USER", "root")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD", "QWer12@*")
        self.DB_NAME = os.getenv("DB_NAME", "farm_db")

        # Gemini settings
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAE0oIus2UKhuI3MdDDbvqlZB03c-WOvKs")
        self.GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

        # API settings
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", 8000))
        self.DEBUG = os.getenv("DEBUG", "False").lower() == "true"

        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings() 
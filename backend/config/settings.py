from decouple import config

# Example settings
DATABASE_URL = config("DATABASE_URL", default="sqlite:///./test.db")
OPEN_AI_ORG = config("OPEN_AI_ORG")
OPEN_AI_KEY = config("OPEN_AI_KEY")

print(f"Loaded settings: {DATABASE_URL}, {OPEN_AI_ORG}, {OPEN_AI_KEY}")  # Debugging

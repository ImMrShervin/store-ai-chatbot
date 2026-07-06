import sys
from dotenv import load_dotenv

load_dotenv()

from app import create_app 
from app.config import Config 

try:
    Config.validate()
except ValueError as e:
    print(str(e))
    print("👉 Copy .env.example to .env and fill in GROQ_API_KEY")
    sys.exit(1)

app = create_app()

if __name__ == "__main__":
    print("=" * 60)
    print(f"🚀 Store Chatbot running on http://{Config.HOST}:{Config.PORT}")
    print(f"🤖 Model: {Config.GROQ_MODEL}")
    print(f"📁 Store config: {Config.STORE_CONFIG_PATH}")
    print(f"💾 Database:     {Config.DATABASE_PATH}")
    print("=" * 60)
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=(Config.FLASK_ENV == "development"),
    )

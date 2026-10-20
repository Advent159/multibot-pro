# =====================================================================
# MultiBot Pro - Configuration Loader
# =====================================================================
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# ============ DISCORD ============
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DISCORD_PREFIX = os.getenv("DISCORD_PREFIX", "!")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID", "")

# ============ TELEGRAM ============
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID", "")

# ============ DATABASE ============
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/bot.db")

# ============ BOT INFO ============
BOT_NAME = os.getenv("BOT_NAME", "MultiBot Pro")
BOT_VERSION = os.getenv("BOT_VERSION", "1.0.0")

# ============ AI (GROQ) ============
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "1024"))
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))


def validate_config(platform: str = "discord"):
    """Validasi config dengan cek placeholder."""
    errors = []

    placeholders = [
        "isi_token_discord_disini",
        "isi_token_telegram_disini",
        "your_discord_token_here",
        "your_telegram_token_here",
        "",
    ]

    if platform == "discord":
        if not DISCORD_TOKEN or DISCORD_TOKEN in placeholders:
            errors.append("DISCORD_TOKEN belum diisi di .env (masih placeholder)")

    if platform == "telegram":
        if not TELEGRAM_TOKEN or TELEGRAM_TOKEN in placeholders:
            errors.append("TELEGRAM_TOKEN belum diisi di .env (masih placeholder)")

    if errors:
        print("❌ ERROR KONFIGURASI:")
        for err in errors:
            print(f"   • {err}")
        print("\n💡 Solusi:")
        print("   1. Buka file .env")
        print("   2. Isi token yang diperlukan dengan token ASLI")
        print("   3. Jangan pakai placeholder")
        return False

    return True


if __name__ == "__main__":
    print("=" * 60)
    print(f"🤖 {BOT_NAME} v{BOT_VERSION}")
    print("=" * 60)
    print(f"Discord Token  : {'✅ Ada' if DISCORD_TOKEN else '❌ Kosong'}")
    print(f"Telegram Token : {'✅ Ada' if TELEGRAM_TOKEN else '❌ Kosong'}")
    print(f"Database Path  : {DATABASE_PATH}")
    print(f"Groq API Key   : {'✅ Ada' if GROQ_API_KEY else '❌ Kosong'}")
    print(f"Groq Model     : {GROQ_MODEL}")
    print("=" * 60)
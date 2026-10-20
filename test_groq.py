import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

key = os.getenv("GROQ_API_KEY", "")

print("=" * 60)
print("🔍 CEK GROQ API KEY")
print("=" * 60)

if not key:
    print("❌ GROQ_API_KEY kosong di .env")
    exit(1)

print(f"Format key  : {'✅ Valid' if key.startswith('gsk_') else '❌ Tidak valid (harus gsk_...)'}")
print(f"Panjang     : {len(key)} karakter")
print(f"Preview     : {key[:15]}...{key[-10:]}")

# Test API call
try:
    client = Groq(api_key=key)
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": "Katakan 'OK' kalau kamu berfungsi."}],
        max_tokens=20,
    )
    print(f"Response    : ✅ {response.choices[0].message.content}")
    print("=" * 60)
    print("🎉 API KEY VALID!")
except Exception as e:
    print(f"Response    : ❌ Error: {e}")
    print("=" * 60)
    print("⚠️ API key ada masalah — cek di console.groq.com")
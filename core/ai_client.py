# =====================================================================
# MultiBot Pro - AI Client (Groq)
# Wrapper untuk Groq API dengan conversation memory + user context
# =====================================================================
import os
import sys
from groq import Groq

# Add parent dir ke path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.config import GROQ_API_KEY, GROQ_MODEL, AI_MAX_TOKENS, AI_TEMPERATURE


class AIClient:
    """Wrapper untuk Groq API."""

    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("❌ GROQ_API_KEY tidak ada di .env!")

        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL
        self.max_tokens = AI_MAX_TOKENS
        self.temperature = AI_TEMPERATURE

        # Memory: simpan history per user
        self.conversation_history = {}
        self.max_history = 10  # simpan 10 pasang pesan (user+bot)

    # ============ CHAT (dengan memory + user context) ============
    def chat(self, user_id, message, system_prompt=None, use_memory=True, user_context=None):
        """
        Chat dengan AI. Bisa dengan memory atau tanpa.

        Args:
            user_id: ID user (untuk memory)
            message: Pesan user
            system_prompt: Custom system prompt (opsional)
            use_memory: True = AI ingat percakapan, False = one-shot
            user_context: Dict berisi info user (nama, server, dll)
        """
        try:
            # System prompt default
            if not system_prompt:
                base_prompt = (
                    "Kamu adalah MultiBot Pro, asisten Discord yang cerdas, ramah, dan santai. "
                    "Jawab dengan singkat (max 3 paragraf), ramah, pakai emoji secukupnya. "
                    "Kalau ditanya dalam Bahasa Indonesia, jawab pakai Bahasa Indonesia."
                )
            else:
                base_prompt = system_prompt

            # Tambahkan konteks user ke system prompt
            if user_context:
                context_lines = []
                if user_context.get("name"):
                    context_lines.append(f"Nama user yang sedang chat: {user_context['name']}")
                if user_context.get("display_name"):
                    context_lines.append(f"Display name: {user_context['display_name']}")
                if user_context.get("discriminator"):
                    context_lines.append(f"Discord tag: {user_context['discriminator']}")
                if user_context.get("server"):
                    context_lines.append(f"Server Discord: {user_context['server']}")
                if user_context.get("roles"):
                    context_lines.append(f"Role di server: {', '.join(user_context['roles'])}")
                if user_context.get("joined_at"):
                    context_lines.append(f"Bergabung server sejak: {user_context['joined_at']}")

                if context_lines:
                    base_prompt += "\n\n=== INFO USER YANG SEDANG CHAT ===\n" + "\n".join(context_lines)
                    base_prompt += (
                        "\n\nGunakan info di atas untuk personalisasi jawaban. "
                        "Panggil user dengan namanya saat menyapa atau menjawab!"
                    )

            # Build messages
            messages = [{"role": "system", "content": base_prompt}]

            # Tambah history kalau use_memory
            if use_memory and str(user_id) in self.conversation_history:
                messages.extend(self.conversation_history[str(user_id)])

            # Tambah pesan baru
            messages.append({"role": "user", "content": message})

            # Request ke Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            reply = response.choices[0].message.content

            # Simpan ke history
            if use_memory:
                if str(user_id) not in self.conversation_history:
                    self.conversation_history[str(user_id)] = []

                self.conversation_history[str(user_id)].append({"role": "user", "content": message})
                self.conversation_history[str(user_id)].append({"role": "assistant", "content": reply})

                # Batasi history (max 10 pasang)
                max_msgs = self.max_history * 2
                if len(self.conversation_history[str(user_id)]) > max_msgs:
                    self.conversation_history[str(user_id)] = \
                        self.conversation_history[str(user_id)][-max_msgs:]

            return reply

        except Exception as e:
            return f"❌ Error AI: {str(e)}"

    # ============ GENERATE (tanpa memory / one-shot) ============
    def generate(self, prompt, system_prompt=None, max_tokens=None):
        """Generate text tanpa memory (one-shot)."""
        try:
            if not system_prompt:
                system_prompt = "Kamu adalah asisten yang membantu dan cerdas."

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens or self.max_tokens,
                temperature=self.temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Error: {str(e)}"

    # ============ CLEAR MEMORY ============
    def clear_memory(self, user_id):
        """Hapus history percakapan user."""
        if str(user_id) in self.conversation_history:
            del self.conversation_history[str(user_id)]
            return True
        return False

    # ============ GET STATS ============
    def get_stats(self):
        """Info tentang AI client."""
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "active_conversations": len(self.conversation_history),
        }


# ============ SINGLETON ============
_ai_instance = None


def get_ai():
    """Get singleton AI client."""
    global _ai_instance
    if _ai_instance is None:
        _ai_instance = AIClient()
    return _ai_instance


# ============ TEST ============
if __name__ == "__main__":
    print("=" * 60)
    print("🤖 Testing Groq AI Client")
    print("=" * 60)

    try:
        ai = get_ai()
        stats = ai.get_stats()
        print(f"📊 Model       : {stats['model']}")
        print(f"📊 Max Tokens  : {stats['max_tokens']}")
        print(f"📊 Temperature : {stats['temperature']}")
        print("=" * 60)

        # Test 1: Simple chat
        print("\n🧪 Test 1: Simple chat")
        print("-" * 60)
        reply = ai.chat("test_user", "Siapa kamu? Jawab singkat max 2 kalimat.")
        print(f"AI: {reply}")

        # Test 2: Chat dengan user context
        print("\n🧪 Test 2: Chat dengan user context")
        print("-" * 60)
        context = {
            "name": "Alek",
            "display_name": "Just call me Alek.",
            "server": "Sekte Titik Koma",
            "roles": ["Roblox", "Kav"],
            "joined_at": "20 September 2025"
        }
        reply = ai.chat("test_user2", "Siapa aku?", user_context=context)
        print(f"AI: {reply}")

        # Test 3: Chat dengan memory
        print("\n🧪 Test 3: Chat dengan memory")
        print("-" * 60)
        ai.chat("test_user", "Nama saya Alek.")
        reply = ai.chat("test_user", "Siapa nama saya?")
        print(f"AI: {reply}")

        # Test 4: Clear memory
        print("\n🧪 Test 4: Clear memory")
        print("-" * 60)
        if ai.clear_memory("test_user"):
            print("✅ Memory dihapus")
        else:
            print("❌ Tidak ada memory")

        print("\n" + "=" * 60)
        print("🎉 SEMUA TEST BERHASIL!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 Solusi:")
        print("   1. Pastikan GROQ_API_KEY ada di .env")
        print("   2. Pastikan API key valid dari console.groq.com")
        print("   3. Cek koneksi internet")
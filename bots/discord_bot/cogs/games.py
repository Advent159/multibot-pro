# =====================================================================
# MultiBot Pro - Mini Games Cog
# =====================================================================
import discord
from discord.ext import commands
import random
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from core.database import add_points, record_game


class Games(commands.Cog):
    """🎮 Mini Games Collection"""

    def __init__(self, bot):
        self.bot = bot

    # ============ GAME 1: DICE ROLL ============
    @commands.command(name="roll", aliases=["dadu"])
    async def roll(self, ctx, sisi: int = 6):
        """🎲 Roll dadu (default 6). Contoh: !roll 20"""
        if sisi < 2 or sisi > 1000:
            await ctx.send("❌ Sisi dadu harus antara 2 - 1000")
            return
        hasil = random.randint(1, sisi)
        embed = discord.Embed(
            title=f"🎲 Roll Dadu D{sisi}",
            description=f"Hasil: **{hasil}**",
            color=0x3498db
        )
        embed.set_footer(text=f"Rolled by {ctx.author.name}")
        await ctx.send(embed=embed)
        record_game(ctx.author.id, won=(hasil >= sisi // 2))

    # ============ GAME 2: COIN FLIP ============
    @commands.command(name="coinflip", aliases=["cf", "koin"])
    async def coinflip(self, ctx):
        """🪙 Lempar koin — Heads or Tails"""
        hasil = random.choice(["Heads", "Tails"])
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"Hasil: **{hasil}**",
            color=0xf1c40f
        )
        await ctx.send(embed=embed)

    # ============ GAME 3: ROCK PAPER SCISSORS ============
    @commands.command(name="rps", aliases=["suten"])
    async def rps(self, ctx, pilihan: str):
        """✊✋✌️ Rock Paper Scissors. Contoh: !rps rock"""
        p = pilihan.lower()
        mapping = {
            "rock": "🪨", "batu": "🪨", "r": "🪨",
            "paper": "📄", "kertas": "📄", "p": "📄",
            "scissors": "✌️", "gunting": "✌️", "s": "✌️"
        }
        # Normalize
        player_key = None
        if p in ("rock", "batu", "r"):
            player_key = "rock"
        elif p in ("paper", "kertas", "p"):
            player_key = "paper"
        elif p in ("scissors", "gunting", "s"):
            player_key = "scissors"

        if not player_key:
            await ctx.send("❌ Pilihan tidak valid! Pilih: `rock`, `paper`, atau `scissors`")
            return

        bot_choice = random.choice(["rock", "paper", "scissors"])
        rules = {"rock": "scissors", "scissors": "paper", "paper": "rock"}

        if player_key == bot_choice:
            result = "🤝 **SERI!**"
            color = 0x95a5a6
            won = None
        elif rules[player_key] == bot_choice:
            result = "🎉 **KAMU MENANG!** (+10 pts)"
            color = 0x2ecc71
            won = True
        else:
            result = "😢 **KAMU KALAH!** (-5 pts)"
            color = 0xe74c3c
            won = False

        embed = discord.Embed(title="✊✋✌️ Rock Paper Scissors", color=color)
        embed.add_field(name="Kamu", value=f"{mapping[player_key]} {player_key.title()}", inline=True)
        embed.add_field(name="Bot", value=f"{mapping[bot_choice]} {bot_choice.title()}", inline=True)
        embed.add_field(name="Hasil", value=result, inline=False)
        await ctx.send(embed=embed)

        if won is True:
            add_points(ctx.author.id, 10, "rps", "win")
            record_game(ctx.author.id, won=True)
        elif won is False:
            add_points(ctx.author.id, -5, "rps", "lose")
            record_game(ctx.author.id, won=False)

    # ============ GAME 4: 8BALL ============
    @commands.command(name="8ball", aliases=["ask"])
    async def eightball(self, ctx, *, pertanyaan: str):
        """🎱 Magic 8-Ball. Contoh: !8ball Apakah aku sukses?"""
        responses = [
            "✅ Tentu saja!", "✅ Sudah pasti!", "✅ Tanpa keraguan!",
            "✅ Ya, lakukan sekarang!", "✅ Percaya pada diri sendiri!",
            "🤔 Mungkin saja...", "🤔 Coba tanya lagi nanti",
            "🤔 Tidak bisa diprediksi sekarang",
            "❌ Jangan harap", "❌ Jawabannya TIDAK",
            "❌ Sangat diragukan", "❌ Cari opsi lain"
        ]
        jawaban = random.choice(responses)
        embed = discord.Embed(title="🎱 Magic 8-Ball", color=0x9b59b6)
        embed.add_field(name="❓ Pertanyaan", value=pertanyaan, inline=False)
        embed.add_field(name="💬 Jawaban", value=jawaban, inline=False)
        embed.set_footer(text=f"Asked by {ctx.author.name}")
        await ctx.send(embed=embed)

    # ============ GAME 5: SLOTS ============
    @commands.command(name="slots", aliases=["slot"])
    async def slots(self, ctx):
        """🎰 Slot Machine — coba keberuntunganmu!"""
        symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣", "⭐"]
        weights = [30, 25, 20, 15, 5, 3, 2]
        result = random.choices(symbols, weights=weights, k=3)

        if result[0] == result[1] == result[2]:
            if result[0] == "7️⃣":
                prize, msg, color = 500, "🎉🎉🎉 **JACKPOT 7️⃣! +500 pts!**", 0xf1c40f
            elif result[0] == "💎":
                prize, msg, color = 200, "💎💎💎 **DIAMOND! +200 pts!**", 0x3498db
            elif result[0] == "⭐":
                prize, msg, color = 150, "⭐⭐⭐ **STAR! +150 pts!**", 0x9b59b6
            else:
                prize, msg, color = 50, f"✅ **3 {result[0]}! +50 pts!**", 0x2ecc71
        elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
            prize, msg, color = 10, "😊 **2 sama! +10 pts!**", 0xf39c12
        else:
            prize, msg, color = -5, "😢 **Tidak ada yang sama... -5 pts**", 0xe74c3c

        embed = discord.Embed(
            title="🎰 Slot Machine",
            description=f"**{' '.join(result)}**\n\n{msg}",
            color=color
        )
        embed.set_footer(text=f"Played by {ctx.author.name}")
        await ctx.send(embed=embed)

        add_points(ctx.author.id, prize, "slots", "win" if prize > 0 else "lose")
        record_game(ctx.author.id, won=(prize > 0))

    # ============ GAME 6: TRIVIA ============
    @commands.command(name="trivia", aliases=["kuis"])
    async def trivia(self, ctx):
        """🧠 Trivia Quiz — jawab pertanyaan!"""
        questions = [
            {"q": "Ibu kota Indonesia?", "a": ["jakarta", "jkt"], "correct": "Jakarta"},
            {"q": "Berapa 15 x 8?", "a": ["120"], "correct": "120"},
            {"q": "Planet terdekat matahari?", "a": ["merkurius", "mercury"], "correct": "Merkurius"},
            {"q": "Presiden pertama Indonesia?", "a": ["soekarno", "sukarno"], "correct": "Soekarno"},
            {"q": "Hewan tercepat di darat?", "a": ["cheetah", "citah"], "correct": "Cheetah"},
            {"q": "Berapa sisi segitiga?", "a": ["3", "tiga"], "correct": "3"},
            {"q": "Warna langit cerah?", "a": ["biru", "blue"], "correct": "Biru"},
            {"q": "100 / 4 = ?", "a": ["25"], "correct": "25"},
            {"q": "Kapan Indonesia merdeka? (tahun)", "a": ["1945"], "correct": "1945"},
            {"q": "Berapa jumlah pemain sepak bola 1 tim?", "a": ["11", "sebelas"], "correct": "11"},
        ]

        q = random.choice(questions)
        embed = discord.Embed(
            title="🧠 Trivia Quiz",
            description=f"**{q['q']}**\n\n⏰ Kamu punya 15 detik!",
            color=0x3498db
        )
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for("message", timeout=15.0, check=check)
            jawaban = msg.content.lower().strip()

            if jawaban in q["a"]:
                embed = discord.Embed(
                    title="✅ BENAR!",
                    description=f"Jawaban: **{q['correct']}**\n💰 +25 pts!",
                    color=0x2ecc71
                )
                add_points(ctx.author.id, 25, "trivia", "win")
                record_game(ctx.author.id, won=True)
            else:
                embed = discord.Embed(
                    title="❌ SALAH!",
                    description=f"Jawaban: **{q['correct']}**\n💸 -5 pts",
                    color=0xe74c3c
                )
                add_points(ctx.author.id, -5, "trivia", "lose")
                record_game(ctx.author.id, won=False)

            await ctx.send(embed=embed)

        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏰ WAKTU HABIS!",
                description=f"Jawaban: **{q['correct']}**",
                color=0x95a5a6
            )
            await ctx.send(embed=embed)

    # ============ GAME 7: D20 ============
    @commands.command(name="d20", aliases=["dnd"])
    async def d20(self, ctx):
        """🎲 D20 Roll — buat yang main D&D"""
        hasil = random.randint(1, 20)
        if hasil == 20:
            title, color = "🌟 CRITICAL SUCCESS!", 0xf1c40f
        elif hasil == 1:
            title, color = "💀 CRITICAL FAIL!", 0xe74c3c
        elif hasil >= 15:
            title, color = "✨ Great Roll!", 0x2ecc71
        elif hasil >= 10:
            title, color = "👍 Good Roll", 0x3498db
        else:
            title, color = "😐 Meh...", 0x95a5a6

        embed = discord.Embed(
            title=title,
            description=f"# 🎲 **{hasil}**",
            color=color
        )
        embed.set_footer(text=f"Rolled by {ctx.author.name}")
        await ctx.send(embed=embed)

    # ============ GAME 8: GUESS NUMBER ============
    @commands.command(name="guess")
    async def guess(self, ctx, angka: int = None):
        """🎯 Tebak angka 1-100 (bot pilih angka random)"""
        if angka is None:
            await ctx.send("🎯 **Cara main:** bot pilih angka 1-100. Kamu tebak pakai `!guess [angka]`.\nContoh: `!guess 50`")
            # Simpan angka random di memory
            secret = random.randint(1, 100)
            ctx.bot._guess_answers = getattr(ctx.bot, "_guess_answers", {})
            ctx.bot._guess_answers[ctx.author.id] = secret
            await ctx.send("✨ Angka sudah dipilih! Sekarang tebak pakai `!guess [angka]`")
            return

        answers = getattr(ctx.bot, "_guess_answers", {})
        if ctx.author.id not in answers:
            await ctx.send("❌ Ketik `!guess` dulu untuk mulai game.")
            return

        secret = answers[ctx.author.id]

        if angka < secret:
            await ctx.send(f"📈 **{angka}** terlalu **KECIL**! Coba lagi.")
        elif angka > secret:
            await ctx.send(f"📉 **{angka}** terlalu **BESAR**! Coba lagi.")
        else:
            await ctx.send(f"🎉 **BENAR!** Angkanya **{secret}**! +50 pts!")
            add_points(ctx.author.id, 50, "guess", "win")
            record_game(ctx.author.id, won=True)
            del answers[ctx.author.id]


async def setup(bot):
    await bot.add_cog(Games(bot))
# =====================================================================
# MultiBot Pro - Fun Commands Cog
# =====================================================================
import discord
from discord.ext import commands
import random
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


class Fun(commands.Cog):
    """🎉 Fun Commands — jokes, quotes, dll"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="joke", aliases=["lucu"])
    async def joke(self, ctx):
        """😂 Random dad joke"""
        jokes = [
            "Kenapa programmer suka kopi? Karena Java-nya! ☕",
            "Kenapa komputer gak bisa masuk angin? Karena takut virus! 🦠",
            "Apa bedanya programmer dan hacker? Kalau hacker yang jahat, kalau programmer yang capek 😂",
            "Kenapa lampu gak pernah tidur? Karena dia selalu ON! 💡",
            "Kenapa buku matematika selalu sedih? Karena penuh dengan masalah 📚",
            "Kenapa aku gak bisa ngoding tanpa internet? Karena Google adalah pacarku 😘",
        ]
        await ctx.send(f"😂 {random.choice(jokes)}")

    @commands.command(name="quote", aliases=["motivasi"])
    async def quote(self, ctx):
        """💪 Random motivational quote"""
        quotes = [
            "💪 **Jangan berhenti. Setiap langkah kecil mendekatkanmu ke tujuan.**",
            "🌟 **Kesuksesan dimulai dari keberanian mencoba.**",
            "🚀 **Kode yang buruk hari ini, lebih baik dari kode sempurna yang tidak pernah dibuat.**",
            "📚 **Setiap error adalah pelajaran.**",
            "⚡ **Belajar hari ini, memimpin esok hari.**",
            "🎯 **Fokus pada tujuan, bukan hambatan.**",
        ]
        await ctx.send(random.choice(quotes))

    @commands.command(name="fact", aliases=["fakta"])
    async def fact(self, ctx):
        """🧠 Random fun fact"""
        facts = [
            "🐙 Gurita punya 3 jantung dan darahnya biru!",
            "🍯 Madu tidak pernah basi — ditemukan di makam Mesir berumur 3000 tahun masih bisa dimakan.",
            "🌌 Bintang neutron bisa memutar 600 kali per detik!",
            "🐜 Ada lebih banyak semut di bumi daripada manusia.",
            "🎮 Game pertama bernama 'Tennis for Two' tahun 1958.",
            "🇮🇩 Indonesia punya 17.000+ pulau — cuma 6.000 yang berpenghuni.",
        ]
        await ctx.send(f"🧠 {random.choice(facts)}")

    @commands.command(name="meme")
    async def meme(self, ctx):
        """😆 Random meme text"""
        memes = [
            "When your code works but you don't know why 🤔",
            "Me: I'll fix bugs tomorrow\nBugs: 👀",
            "Python: Simple and readable\nJava: Hold my coffee ☕",
            "Friday deploy: bold move 🚀",
            "When client says 'just a small change' 😱",
        ]
        await ctx.send(random.choice(memes))

    @commands.command(name="ship")
    async def ship(self, ctx, member1: discord.Member = None, member2: discord.Member = None):
        """💕 Cek compatibility 2 user"""
        if not member1:
            member1 = ctx.author
        if not member2:
            member2 = ctx.author

        percentage = random.randint(0, 100)
        if percentage >= 80:
            emoji, msg = "💕", "Jodoh nih!"
        elif percentage >= 60:
            emoji, msg = "💖", "Lumayan cocok!"
        elif percentage >= 40:
            emoji, msg = "❤️", "Bisa dicoba"
        elif percentage >= 20:
            emoji, msg = "💔", "Hmm..."
        else:
            emoji, msg = "💀", "Jangan deh..."

        bar = "█" * (percentage // 5) + "░" * (20 - percentage // 5)

        embed = discord.Embed(
            title=f"{emoji} Love Calculator",
            description=f"**{member1.name}** ❤️ **{member2.name}**\n\n`{bar}` **{percentage}%**\n\n_{msg}_",
            color=0xff6b9d
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Fun(bot))
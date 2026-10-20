# =====================================================================
# MultiBot Pro - Economy System Cog
# =====================================================================
import discord
from discord.ext import commands
from datetime import datetime, timedelta
import sys
import os
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from core.database import (
    get_user, add_points, get_leaderboard, get_stats, get_connection
)


class Economy(commands.Cog):
    """💰 Economy — points, leaderboard, daily reward"""

    def __init__(self, bot):
        self.bot = bot

    # ============ BALANCE ============
    @commands.command(name="balance", aliases=["bal", "saldo"])
    async def balance(self, ctx, member: discord.Member = None):
        """💰 Cek saldo poin. Contoh: !balance atau !balance @user"""
        target = member or ctx.author
        user = get_user(target.id)

        embed = discord.Embed(
            title=f"💰 Saldo {target.name}",
            color=0xf1c40f
        )
        embed.add_field(name="🪙 Points", value=f"**{user['points']:,}**", inline=True)
        embed.add_field(name="🎮 Games", value=f"`{user['games_played']}`", inline=True)
        embed.add_field(name="🏆 Wins", value=f"`{user['games_won']}`", inline=True)
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)

    # ============ LEADERBOARD ============
    @commands.command(name="leaderboard", aliases=["lb", "top"])
    async def leaderboard(self, ctx):
        """🏆 Top 10 user dengan poin tertinggi"""
        top = get_leaderboard(10)
        if not top:
            await ctx.send("📭 Belum ada data user.")
            return

        embed = discord.Embed(
            title="🏆 Leaderboard — Top 10",
            color=0xf1c40f,
            timestamp=datetime.now()
        )

        medals = ["🥇", "🥈", "🥉"]
        desc = ""
        for i, user in enumerate(top):
            medal = medals[i] if i < 3 else f"`#{i+1}`"
            desc += f"{medal} **{user['username']}** — `{user['points']:,}` pts ({user['games_won']}W)\n"

        embed.description = desc
        embed.set_footer(text="Kumpulkan poin dengan main games!")
        await ctx.send(embed=embed)

    # ============ DAILY ============
    @commands.command(name="daily", aliases=["harian"])
    async def daily(self, ctx):
        """🎁 Klaim reward harian (sekali per 24 jam)"""
        conn = get_connection()
        cursor = conn.cursor()
        user_id = str(ctx.author.id)
        get_user(user_id)

        cursor.execute("""
            SELECT played_at FROM game_history
            WHERE user_id = ? AND game_type = 'daily'
            ORDER BY played_at DESC LIMIT 1
        """, (user_id,))
        last = cursor.fetchone()

        if last:
            last_time = datetime.fromisoformat(last["played_at"])
            cooldown = timedelta(hours=24)
            if datetime.now() - last_time < cooldown:
                remaining = cooldown - (datetime.now() - last_time)
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60
                await ctx.send(f"⏰ Sudah klaim hari ini! Coba lagi dalam **{hours}j {minutes}m**")
                conn.close()
                return

        reward = random.randint(50, 150)
        add_points(user_id, reward, "daily", "reward")

        embed = discord.Embed(
            title="🎁 Daily Reward!",
            description=f"Kamu dapat **{reward} poin**! 🪙",
            color=0x2ecc71
        )
        embed.set_footer(text="Kembali besok untuk reward lagi!")
        await ctx.send(embed=embed)
        conn.close()

    # ============ TRANSFER ============
    @commands.command(name="transfer", aliases=["tf", "kirim"])
    async def transfer(self, ctx, member: discord.Member, amount: int):
        """💸 Transfer poin. Contoh: !transfer @user 100"""
        if member == ctx.author:
            await ctx.send("❌ Tidak bisa transfer ke diri sendiri!")
            return
        if member.bot:
            await ctx.send("❌ Tidak bisa transfer ke bot!")
            return
        if amount <= 0:
            await ctx.send("❌ Jumlah harus > 0!")
            return

        sender = get_user(ctx.author.id)
        if sender["points"] < amount:
            await ctx.send(f"❌ Saldo kurang! Kamu cuma punya **{sender['points']:,}** poin.")
            return

        add_points(ctx.author.id, -amount, "transfer_out", f"to {member.name}")
        add_points(member.id, amount, "transfer_in", f"from {ctx.author.name}")

        embed = discord.Embed(
            title="💸 Transfer Berhasil!",
            description=f"**{ctx.author.mention}** → **{member.mention}**\n\n💰 Jumlah: **{amount:,} poin**",
            color=0x2ecc71
        )
        await ctx.send(embed=embed)

    # ============ STATS ============
    @commands.command(name="stats", aliases=["statistik"])
    async def stats(self, ctx, member: discord.Member = None):
        """📊 Lihat statistik lengkap"""
        target = member or ctx.author
        user = get_stats(target.id)

        win_rate = 0
        if user["games_played"] > 0:
            win_rate = (user["games_won"] / user["games_played"]) * 100

        embed = discord.Embed(
            title=f"📊 Stats — {target.name}",
            color=0x3498db,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="🪙 Points", value=f"`{user['points']:,}`", inline=True)
        embed.add_field(name="🎮 Total Games", value=f"`{user['games_played']}`", inline=True)
        embed.add_field(name="🏆 Wins", value=f"`{user['games_won']}`", inline=True)
        embed.add_field(name="😢 Losses", value=f"`{user['games_lost']}`", inline=True)
        embed.add_field(name="📈 Win Rate", value=f"`{win_rate:.1f}%`", inline=True)
        await ctx.send(embed=embed)

    # ============ GIVE (Admin) ============
    @commands.command(name="give")
    @commands.has_permissions(administrator=True)
    async def give(self, ctx, member: discord.Member, amount: int):
        """🎁 [ADMIN] Kasih poin ke user"""
        add_points(member.id, amount, "admin_give", f"from {ctx.author.name}")
        embed = discord.Embed(
            title="🎁 Admin Give",
            description=f"**{ctx.author.name}** memberi **{amount:,} pts** ke **{member.mention}**",
            color=0xf1c40f
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Economy(bot))
# =====================================================================
# MultiBot Pro - Discord Bot (with Cogs)
# =====================================================================
import discord
from discord.ext import commands
import sys
import os
import asyncio
from datetime import datetime

# Add parent dir ke path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.config import (
    DISCORD_TOKEN, DISCORD_PREFIX, BOT_NAME, BOT_VERSION, validate_config
)
from core.database import init_database

# Validasi config
if not validate_config("discord"):
    sys.exit(1)

# Init database
init_database()

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# Bot setup
bot = commands.Bot(command_prefix=DISCORD_PREFIX, intents=intents, help_command=None)


# ============ EVENTS ============
@bot.event
async def on_ready():
    print("=" * 60)
    print(f"🤖 {BOT_NAME} v{BOT_VERSION}")
    print("=" * 60)
    print(f"✅ Logged in as : {bot.user.name}")
    print(f"🆔 Bot ID       : {bot.user.id}")
    print(f"🌐 Servers      : {len(bot.guilds)}")
    print(f"👥 Total Users  : {sum(g.member_count for g in bot.guilds)}")
    print(f"⚡ Latency      : {round(bot.latency * 1000)}ms")
    print(f"📦 Loaded Cogs  : {len(bot.cogs)}")
    print(f"🔧 Commands     : {len(bot.commands)}")
    print("=" * 60)
    print("🎮 Games  : !roll !coinflip !rps !8ball !slots !trivia !d20 !guess")
    print("💰 Economy: !balance !leaderboard !daily !transfer !stats !give")
    print("🎉 Fun    : !joke !quote !fact !meme !ship")
    print("🤖 AI     : !ai !code !translate !summarize !roleplay !story !quizai !imagine !whoami !clearai !aistats")
    print("=" * 60)

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{DISCORD_PREFIX}help | {len(bot.guilds)} servers"
        )
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Command tidak ditemukan. Ketik `{DISCORD_PREFIX}help` untuk bantuan.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argument kurang! Ketik `{DISCORD_PREFIX}help {ctx.command.name}` untuk cara pakai.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Kamu tidak punya permission untuk command ini!")
    else:
        await ctx.send(f"❌ Error: `{str(error)}`")
        print(f"[ERROR] {error}")


# ============ BASIC COMMANDS ============
@bot.command(name="ping")
async def ping(ctx):
    """Cek latency bot"""
    latency = round(bot.latency * 1000)
    emoji = "🟢" if latency < 100 else "🟡" if latency < 200 else "🔴"
    await ctx.send(f"{emoji} Pong! Latency: **{latency}ms**")


@bot.command(name="hello", aliases=["hi", "hai"])
async def hello(ctx):
    """Sapaan dari bot"""
    await ctx.send(f"👋 Halo {ctx.author.mention}! Saya **{BOT_NAME}** v{BOT_VERSION}, siap membantu!")


@bot.command(name="info")
async def info(ctx):
    """Info tentang bot"""
    embed = discord.Embed(
        title=f"🤖 {BOT_NAME}",
        description="One Bot, Many Powers — Discord & Telegram",
        color=0x002B5C,
        timestamp=datetime.now()
    )
    embed.add_field(name="📌 Version", value=f"`v{BOT_VERSION}`", inline=True)
    embed.add_field(name="🌐 Servers", value=f"`{len(bot.guilds)}`", inline=True)
    embed.add_field(name="👥 Users", value=f"`{sum(g.member_count for g in bot.guilds)}`", inline=True)
    embed.add_field(name="⚡ Latency", value=f"`{round(bot.latency * 1000)}ms`", inline=True)
    embed.add_field(name="📦 Cogs", value=f"`{len(bot.cogs)}`", inline=True)
    embed.add_field(name="🔧 Commands", value=f"`{len(bot.commands)}`", inline=True)
    embed.set_footer(text=f"Made with ❤️ | {BOT_NAME}")
    await ctx.send(embed=embed)


@bot.command(name="help")
async def help_cmd(ctx, *, command_name: str = None):
    """Bantuan command"""
    if command_name:
        cmd = bot.get_command(command_name)
        if not cmd:
            await ctx.send(f"❌ Command `{command_name}` tidak ditemukan.")
            return
        embed = discord.Embed(
            title=f"📖 Help: {DISCORD_PREFIX}{cmd.name}",
            description=cmd.help or "Tidak ada deskripsi.",
            color=0x002B5C
        )
        if cmd.aliases:
            embed.add_field(name="🔗 Aliases", value=", ".join(f"`{DISCORD_PREFIX}{a}`" for a in cmd.aliases))
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title=f"📖 {BOT_NAME} — Command List",
        description=f"Prefix: `{DISCORD_PREFIX}` | Total: `{len(bot.commands)}` commands",
        color=0x002B5C
    )
    embed.add_field(
        name="🎮 Games",
        value=f"`{DISCORD_PREFIX}roll` `{DISCORD_PREFIX}coinflip` `{DISCORD_PREFIX}rps` `{DISCORD_PREFIX}8ball`\n"
              f"`{DISCORD_PREFIX}slots` `{DISCORD_PREFIX}trivia` `{DISCORD_PREFIX}d20` `{DISCORD_PREFIX}guess`",
        inline=False
    )
    embed.add_field(
        name="💰 Economy",
        value=f"`{DISCORD_PREFIX}balance` `{DISCORD_PREFIX}leaderboard` `{DISCORD_PREFIX}daily`\n"
              f"`{DISCORD_PREFIX}transfer` `{DISCORD_PREFIX}stats`",
        inline=False
    )
    embed.add_field(
        name="🎉 Fun",
        value=f"`{DISCORD_PREFIX}joke` `{DISCORD_PREFIX}quote` `{DISCORD_PREFIX}fact` `{DISCORD_PREFIX}meme` `{DISCORD_PREFIX}ship`",
        inline=False
    )
    embed.add_field(
        name="🤖 AI (Powered by Groq)",
        value=(
            f"`{DISCORD_PREFIX}ai` — Chat dengan AI\n"
            f"`{DISCORD_PREFIX}code` — Bantuan coding\n"
            f"`{DISCORD_PREFIX}translate` — Translate text\n"
            f"`{DISCORD_PREFIX}summarize` — Ringkas text\n"
            f"`{DISCORD_PREFIX}roleplay` — AI jadi karakter\n"
            f"`{DISCORD_PREFIX}story` — Bikin cerita\n"
            f"`{DISCORD_PREFIX}quizai` — AI bikin quiz\n"
            f"`{DISCORD_PREFIX}imagine` — Prompt gambar\n"
            f"`{DISCORD_PREFIX}whoami` — Info user\n"
            f"`{DISCORD_PREFIX}clearai` — Reset memory AI\n"
            f"`{DISCORD_PREFIX}aistats` — Info AI client"
        ),
        inline=False
    )
    embed.add_field(
        name="🔧 Basic",
        value=f"`{DISCORD_PREFIX}ping` `{DISCORD_PREFIX}hello` `{DISCORD_PREFIX}info` `{DISCORD_PREFIX}help`",
        inline=False
    )
    embed.set_footer(text=f"Ketik {DISCORD_PREFIX}help [command] untuk detail")
    await ctx.send(embed=embed)


# ============ LOAD COGS ============
async def load_cogs():
    cogs = ["games", "economy", "fun", "ai"]
    for cog in cogs:
        try:
            await bot.load_extension(f"bots.discord_bot.cogs.{cog}")
            print(f"✅ Loaded cog: {cog}")
        except Exception as e:
            print(f"❌ Failed to load cog {cog}: {e}")


# ============ RUN ============
async def main():
    async with bot:
        await load_cogs()
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    print(f"🚀 Starting {BOT_NAME}...")
    try:
        asyncio.run(main())
    except discord.LoginFailure:
        print("❌ ERROR: Token Discord tidak valid! Cek .env")
    except KeyboardInterrupt:
        print("\n👋 Bot dihentikan.")
    except Exception as e:
        print(f"❌ ERROR: {e}")
# =====================================================================
# MultiBot Pro - AI Cog (Groq + Llama 3.3)
# 11 AI commands — chat, code, translate, roleplay, story, dll
# =====================================================================
import discord
from discord.ext import commands
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
from core.ai_client import get_ai
from core.database import add_points, update_user_info


class AI(commands.Cog):
    """🤖 AI Commands — powered by Groq"""

    def __init__(self, bot):
        self.bot = bot
        self.ai = get_ai()

    # ============ COMMAND 1: !ai — CHAT ============
    @commands.command(name="ai", aliases=["aiask", "chat"])
    async def ai_chat(self, ctx, *, pesan: str):
        """🤖 Chat dengan AI. Contoh: !ai Apa itu Python?"""
        async with ctx.typing():
            msg = await ctx.send("🤔 **AI sedang berpikir...**")

            try:
                # === Ambil info user Discord ===
                author = ctx.author
                user_context = {
                    "name": author.name,
                    "display_name": author.display_name,
                    "discriminator": str(author.discriminator) if author.discriminator != "0" else "",
                    "id": str(author.id),
                }

                if ctx.guild:
                    user_context["server"] = ctx.guild.name
                    user_context["server_id"] = str(ctx.guild.id)

                    if hasattr(author, "roles"):
                        roles = [r.name for r in author.roles if r.name != "@everyone"][:5]
                        user_context["roles"] = roles

                    if hasattr(author, "joined_at") and author.joined_at:
                        user_context["joined_at"] = author.joined_at.strftime("%d %B %Y")

                # Update info user ke database
                update_user_info(
                    str(author.id),
                    username=author.name,
                    display_name=author.display_name,
                    server_name=ctx.guild.name if ctx.guild else "DM"
                )

                # === Kirim ke AI ===
                loop = asyncio.get_event_loop()
                reply = await loop.run_in_executor(
                    None,
                    lambda: self.ai.chat(
                        str(ctx.author.id),
                        pesan,
                        user_context=user_context
                    )
                )

                if len(reply) > 1900:
                    reply = reply[:1900] + "..."

                embed = discord.Embed(
                    title="🤖 AI Assistant",
                    description=reply,
                    color=0x9b59b6
                )
                embed.set_footer(text=f"Dijawab untuk {ctx.author.name} • Powered by Groq")
                embed.set_thumbnail(url=self.bot.user.display_avatar.url)

                await msg.edit(content=None, embed=embed)
                add_points(ctx.author.id, 2, "ai_chat", "used")

            except Exception as e:
                await msg.edit(content=f"❌ Error: `{str(e)}`")

    # ============ COMMAND 2: !code ============
    @commands.command(name="code", aliases=["coding", "program"])
    async def code_help(self, ctx, *, request: str):
        """💻 Bantuan coding. Contoh: !code Buat fungsi Python cek bilangan prima"""
        async with ctx.typing():
            msg = await ctx.send("💻 **AI sedang coding...**")

            system = (
                "Kamu adalah expert programmer. Bantu user dengan kode yang bersih, "
                "mudah dipahami, dengan komentar. Jawab dalam Bahasa Indonesia. "
                "Format kode pakai code block ```language."
            )

            loop = asyncio.get_event_loop()
            reply = await loop.run_in_executor(
                None,
                lambda: self.ai.generate(request, system_prompt=system, max_tokens=1500)
            )

            if len(reply) > 1900:
                await msg.edit(content="💻 **Kode yang dihasilkan:**")
                chunks = [reply[i:i+1900] for i in range(0, len(reply), 1900)]
                for chunk in chunks[:3]:
                    await ctx.send(f"```\n{chunk}\n```")
            else:
                await msg.edit(content=f"💻 **Kode:**\n```\n{reply}\n```")

            add_points(ctx.author.id, 3, "ai_code", "used")

    # ============ COMMAND 3: !translate ============
    @commands.command(name="translate", aliases=["tr"])
    async def translate(self, ctx, target_lang: str, *, text: str):
        """🌐 Translate text. Contoh: !translate en Halo apa kabar"""
        async with ctx.typing():
            msg = await ctx.send(f"🌐 **Translating ke {target_lang}...**")

            prompt = (
                f"Translate text berikut ke bahasa {target_lang}. "
                f"Cuma kasih hasil terjemahan, jangan ada penjelasan tambahan.\n\n"
                f"Text: {text}"
            )

            loop = asyncio.get_event_loop()
            reply = await loop.run_in_executor(
                None,
                lambda: self.ai.generate(prompt, max_tokens=500)
            )

            embed = discord.Embed(
                title=f"🌐 Translate → {target_lang.upper()}",
                color=0x3498db
            )
            embed.add_field(name="📝 Original", value=text, inline=False)
            embed.add_field(name="✨ Translation", value=reply, inline=False)
            embed.set_footer(text=f"Translated for {ctx.author.name}")

            await msg.edit(content=None, embed=embed)

    # ============ COMMAND 4: !summarize ============
    @commands.command(name="summarize", aliases=["ringkas", "ringkasan"])
    async def summarize(self, ctx, *, text: str):
        """📝 Ringkas text panjang. Contoh: !summarize [text panjang]"""
        async with ctx.typing():
            msg = await ctx.send("📝 **Merangkum...**")

            prompt = f"Ringkas text berikut dalam 3-5 poin penting. Bahasa Indonesia:\n\n{text}"

            loop = asyncio.get_event_loop()
            reply = await loop.run_in_executor(
                None,
                lambda: self.ai.generate(prompt, max_tokens=800)
            )

            embed = discord.Embed(
                title="📝 Ringkasan",
                description=reply,
                color=0x2ecc71
            )
            embed.set_footer(text=f"Summarized for {ctx.author.name}")

            await msg.edit(content=None, embed=embed)

    # ============ COMMAND 5: !roleplay ============
    @commands.command(name="roleplay", aliases=["rp", "act"])
    async def roleplay(self, ctx, character: str, *, message: str = "Perkenalkan dirimu"):
        """🎭 AI jadi karakter tertentu. Contoh: !roleplay pirate Halo kapten!"""
        async with ctx.typing():
            msg = await ctx.send(f"🎭 **AI jadi {character}...**")

            system = (
                f"Kamu sekarang berperan sebagai karakter: **{character}**. "
                f"Jawab SEPENUHNYA sesuai karakter ini. Pakai gaya bicara, kepribadian, "
                f"dan emoji yang sesuai. Jangan keluar karakter. Jawab singkat max 2 paragraf."
            )

            loop = asyncio.get_event_loop()
            reply = await loop.run_in_executor(
                None,
                lambda: self.ai.generate(message, system_prompt=system, max_tokens=600)
            )

            embed = discord.Embed(
                title=f"🎭 Roleplay: {character}",
                description=reply,
                color=0xe74c3c
            )
            embed.set_footer(text=f"Acted by AI for {ctx.author.name}")

            await msg.edit(content=None, embed=embed)

    # ============ COMMAND 6: !story ============
    @commands.command(name="story", aliases=["cerita", "storytelling"])
    async def story(self, ctx, *, prompt: str):
        """📖 Buat cerita pendek. Contoh: !story Naga kecil yang takut api"""
        async with ctx.typing():
            msg = await ctx.send("📖 **Menulis cerita...**")

            system = (
                "Kamu adalah penulis cerita kreatif. Buat cerita pendek (max 200 kata) "
                "yang menarik dengan awal, konflik, dan akhir yang memuaskan. "
                "Pakai bahasa Indonesia yang indah dan imajinatif."
            )

            loop = asyncio.get_event_loop()
            reply = await loop.run_in_executor(
                None,
                lambda: self.ai.generate(prompt, system_prompt=system, max_tokens=500)
            )

            embed = discord.Embed(
                title=f"📖 Cerita: {prompt[:50]}{'...' if len(prompt) > 50 else ''}",
                description=reply,
                color=0x9b59b6
            )
            embed.set_footer(text=f"Story by AI for {ctx.author.name}")

            await msg.edit(content=None, embed=embed)

    # ============ COMMAND 7: !quizai ============
    @commands.command(name="quizai", aliases=["kuisai"])
    async def quiz_ai(self, ctx, *, topic: str = "pengetahuan umum"):
        """🧠 AI bikin quiz otomatis. Contoh: !quizai matematika"""
        async with ctx.typing():
            msg = await ctx.send(f"🧠 **AI bikin quiz tentang {topic}...**")

            prompt = (
                f"Buat 1 pertanyaan quiz tentang {topic} dengan 4 pilihan jawaban (A, B, C, D). "
                f"Format jawaban:\n\n"
                f"**Pertanyaan:** [pertanyaan]\n\n"
                f"**A)** [jawaban]\n**B)** [jawaban]\n**C)** [jawaban]\n**D)** [jawaban]\n\n"
                f"**Jawaban:** [A/B/C/D]\n"
                f"**Penjelasan:** [singkat]"
            )

            loop = asyncio.get_event_loop()
            reply = await loop.run_in_executor(
                None,
                lambda: self.ai.generate(prompt, max_tokens=400)
            )

            embed = discord.Embed(
                title=f"🧠 AI Quiz: {topic.title()}",
                description=reply,
                color=0x3498db
            )
            embed.set_footer(text=f"Quiz by AI for {ctx.author.name}")

            await msg.edit(content=None, embed=embed)

    # ============ COMMAND 8: !clearai ============
    @commands.command(name="clearai", aliases=["resetai", "forget"])
    async def clear_ai(self, ctx):
        """🧹 Hapus memory AI untuk Anda"""
        if self.ai.clear_memory(str(ctx.author.id)):
            embed = discord.Embed(
                title="🧹 Memory Dihapus",
                description="Percakapan AI kamu sudah direset! Mulai dari awal lagi.",
                color=0x95a5a6
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("📭 Tidak ada memory untuk dihapus.")

    # ============ COMMAND 9: !imagine ============
    @commands.command(name="imagine", aliases=["pic", "image"])
    async def imagine(self, ctx, *, prompt: str):
        """🎨 Buat prompt gambar untuk Midjourney/DALL-E.
        Contoh: !imagine kucing pakai topi astronot
        """
        async with ctx.typing():
            msg = await ctx.send("🎨 **AI bikin prompt gambar...**")

            system = (
                "Kamu adalah expert prompt engineer untuk AI image generation "
                "(Midjourney, DALL-E, Stable Diffusion). "
                "Buat prompt dalam Bahasa Inggris yang DETAIL dan artistik. "
                "Format: cuma promptnya saja, tanpa penjelasan tambahan. "
                "Sertakan style, lighting, mood, dan detail teknis."
            )

            loop = asyncio.get_event_loop()
            reply = await loop.run_in_executor(
                None,
                lambda: self.ai.generate(prompt, system_prompt=system, max_tokens=300)
            )

            embed = discord.Embed(
                title="🎨 AI Image Prompt",
                description=f"**Input:** {prompt}\n\n**Prompt:**\n```{reply}```",
                color=0xff6b9d
            )
            embed.set_footer(text="Copy prompt ke Midjourney/DALL-E untuk generate gambar")

            await msg.edit(content=None, embed=embed)

    # ============ COMMAND 10: !aistats ============
    @commands.command(name="aistats", aliases=["aiinfo"])
    async def ai_stats(self, ctx):
        """📊 Info tentang AI client"""
        stats = self.ai.get_stats()

        embed = discord.Embed(
            title="📊 AI Client Stats",
            color=0x9b59b6
        )
        embed.add_field(name="🤖 Model", value=f"`{stats['model']}`", inline=False)
        embed.add_field(name="📏 Max Tokens", value=f"`{stats['max_tokens']}`", inline=True)
        embed.add_field(name="🌡️ Temperature", value=f"`{stats['temperature']}`", inline=True)
        embed.add_field(name="💬 Active Conversations", value=f"`{stats['active_conversations']}`", inline=True)
        embed.set_footer(text="Powered by Groq • Super fast AI")

        await ctx.send(embed=embed)

    # ============ COMMAND 11: !whoami ============
    @commands.command(name="whoami", aliases=["myinfo"])
    async def whoami(self, ctx):
        """👤 Lihat apa yang AI tahu tentang Anda"""
        author = ctx.author

        embed = discord.Embed(
            title="👤 Info User (yang AI tahu)",
            color=0x3498db
        )
        embed.add_field(name="Username", value=f"`{author.name}`", inline=True)
        embed.add_field(name="Display Name", value=f"`{author.display_name}`", inline=True)
        embed.add_field(name="User ID", value=f"`{author.id}`", inline=True)

        if ctx.guild:
            embed.add_field(name="Server", value=f"`{ctx.guild.name}`", inline=False)

            if hasattr(author, "roles"):
                roles = [r.mention for r in author.roles if r.name != "@everyone"]
                if roles:
                    embed.add_field(name="Roles", value=" ".join(roles[:5]), inline=False)

            if hasattr(author, "joined_at") and author.joined_at:
                embed.add_field(
                    name="Bergabung Server",
                    value=f"<t:{int(author.joined_at.timestamp())}:R>",
                    inline=True
                )

        embed.set_thumbnail(url=author.display_avatar.url)
        embed.set_footer(text="AI akan pakai info ini untuk personalisasi jawaban")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AI(bot))
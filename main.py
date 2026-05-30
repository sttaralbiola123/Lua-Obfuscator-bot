import os
import re
import json
import tempfile
import asyncio
from threading import Thread

import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Lua Obfuscator Bot is running!"


def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

_synced = False


def strip_code_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:lua)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def make_temp_text_file(prefix: str, content: str) -> str:
    fd, path = tempfile.mkstemp(prefix=prefix, suffix=".txt")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


async def ask_gemini(prompt: str) -> str:
    if not GEMINI_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY environment variable.")

    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    timeout = aiohttp.ClientTimeout(total=90)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(
            f"{GEMINI_URL}?key={GEMINI_KEY}",
            headers=headers,
            json=body,
        ) as resp:
            raw = await resp.text()

            if resp.status != 200:
                raise RuntimeError(f"Gemini API error {resp.status}: {raw[:500]}")

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                raise RuntimeError("Gemini returned invalid JSON.")

    candidates = data.get("candidates") or []
    if not candidates:
        feedback = data.get("promptFeedback", {})
        block_reason = feedback.get("blockReason")
        if block_reason:
            raise RuntimeError(f"Gemini blocked the request: {block_reason}")
        raise RuntimeError("Gemini returned no candidates.")

    content = candidates[0].get("content", {})
    parts = content.get("parts") or []

    result_text = []
    for part in parts:
        if isinstance(part, dict) and "text" in part:
            result_text.append(part["text"])

    result = "\n".join(result_text).strip()
    if not result:
        raise RuntimeError("Gemini returned an empty response.")

    return result


@bot.event
async def setup_hook():
    global _synced
    if not _synced:
        await bot.tree.sync()
        _synced = True


@bot.event
async def on_ready():
    print(f"✅ Bot ready: {bot.user}")


@bot.tree.command(name="analyze", description="AI mag-eexplain kung ano ginagawa ng Lua code")
@app_commands.describe(code="Lua code na i-aanalyze")
async def analyze_cmd(interaction: discord.Interaction, code: str):
    code = code.strip()
    if not code:
        await interaction.response.send_message("Pakilagay muna ang Lua code.", ephemeral=True)
        return

    loading_embed = discord.Embed(
        title="🔍 Analyzing...",
        description="```Please wait, AI is analyzing your code...```",
        color=0x3498DB,
    )
    loading_embed.set_footer(text="Lua Obfuscator • Powered by Gemini AI")

    await interaction.response.send_message(embed=loading_embed)

    prompt = f"""Analyze this Lua script and explain in simple Filipino/English what it does.
List the main functions, what variables do, and the overall purpose.
Do NOT provide any modified or obfuscated version.

Lua code:
```lua
{code}
```"""

    try:
        result = await ask_gemini(prompt)

        if len(result) > 3800:
            file_path = make_temp_text_file("analysis_", result)
            file_name = os.path.basename(file_path)

            done_embed = discord.Embed(
                title="✅ Analysis Complete!",
                description="Masyadong mahaba ang analysis, naka-save ito sa file.",
                color=0x3498DB,
            )
            done_embed.set_footer(text="Lua Obfuscator • Powered by Gemini AI")

            try:
                await interaction.edit_original_response(
                    embed=done_embed,
                    attachments=[discord.File(file_path, filename=file_name)],
                )
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            done_embed = discord.Embed(
                title="✅ Analysis Complete!",
                description=result,
                color=0x3498DB,
            )
            done_embed.set_footer(text="Lua Obfuscator • Powered by Gemini AI")
            await interaction.edit_original_response(embed=done_embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"```{str(e)}```",
            color=0xFF0000,
        )
        await interaction.edit_original_response(embed=error_embed)


@bot.tree.command(name="obfuscate", description="AI-powered Lua obfuscator")
@app_commands.describe(
    code="Lua code na io-obfuscate",
    level="1=Basic | 2=Medium | 3=Advanced (loadstring layers)"
)
async def obfuscate_cmd(interaction: discord.Interaction, code: str, level: int = 2):
    code = code.strip()
    if not code:
        await interaction.response.send_message("Pakilagay muna ang Lua code.", ephemeral=True)
        return

    if level < 1 or level > 3:
        await interaction.response.send_message("Level dapat 1-3 lang!", ephemeral=True)
        return

    loading_embed = discord.Embed(
        title="⚙️ Obfuscating...",
        description="```Please wait, AI is obfuscating your code...```",
        color=0xFFA500,
    )
    loading_embed.add_field(name="Level", value=f"`{level}`", inline=True)
    loading_embed.add_field(name="Status", value="🔄 Processing...", inline=True)
    loading_embed.set_footer(text="Lua Obfuscator • Powered by Gemini AI")

    await interaction.response.send_message(embed=loading_embed)

    level_instructions = {
        1: "Encode all strings as string.char() byte arrays. Rename variables to random names.",
        2: "Encode all strings as string.char(). Rename all variables/functions to random names. Add junk code lines that do nothing.",
        3: "Encode all strings as string.char(). Rename all variables/functions to random names. Add junk code. Then wrap the ENTIRE obfuscated code inside 3 nested loadstring(string.char(...))() calls."
    }

    prompt = f"""You are a Lua obfuscator. Obfuscate the following Lua code using these techniques:
{level_instructions[level]}

Rules:
- Output ONLY the obfuscated Lua code
- No explanations, no markdown, no code blocks
- Code must still be functional and runnable

Lua code to obfuscate:
{code}"""

    try:
        result = await ask_gemini(prompt)
        result = strip_code_fences(result)

        file_path = make_temp_text_file("obfuscated_", result)
        file_name = os.path.basename(file_path)

        done_embed = discord.Embed(
            title="✅ Obfuscation Complete!",
            description=(
                "Your Lua code has been successfully obfuscated!\n\n"
                "**Tips:**\n"
                "> • Test the file before using it\n"
                "> • Level 3 uses loadstring layers\n"
                "> • Keep the original code as backup"
            ),
            color=0x00FF7F,
        )
        done_embed.add_field(name="Level Used", value=f"`{level}`", inline=True)
        done_embed.add_field(name="File Name", value=f"`{file_name}`", inline=True)
        done_embed.add_field(name="Lines", value=f"`{len(result.splitlines())}`", inline=True)
        done_embed.set_footer(text="Lua Obfuscator • Powered by Gemini AI")

        try:
            await interaction.edit_original_response(
                embed=done_embed,
                attachments=[discord.File(file_path, filename=file_name)],
            )
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"```{str(e)}```",
            color=0xFF0000,
        )
        await interaction.edit_original_response(embed=error_embed)


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise RuntimeError("Missing DISCORD_TOKEN environment variable.")

    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    bot.run(DISCORD_TOKEN)

import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os
import aiohttp
import asyncio
import uuid
import re

app = Flask(__name__)

@app.route('/')
def home():
    return "Lua Obfuscator Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

async def ask_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise Exception("API Key is missing! Paki-check ang environment variables sa Render.")

    # Kasama ang pinakabagong models para sa taong 2026
    models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]
    
    headers = {"Content-Type": "application/json"}
    body = {"contents": [{"parts": [{"text": prompt}]}]}

    async with aiohttp.ClientSession() as session:
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            async with session.post(url, headers=headers, json=body) as resp:
                
                # FIX: Kung hindi 200 OK ang response, i-print ang eksaktong error mula sa Google
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"❌ {model} HTTP {resp.status} Error: {error_text}")
                    continue

                data = await resp.json()

                if "error" in data:
                    print(f"❌ {model} API error: {data['error']['code']} - {data['error']['message']}")
                    continue

                if "candidates" not in data or not data["candidates"]:
                    print(f"❌ {model}: No candidates. Raw response: {data}")
                    continue

                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except KeyError:
                    print(f"❌ {model}: Unexpected JSON format structure.")
                    continue

    raise Exception("All Gemini models failed. Paki-check ang Render Console Logs para sa eksaktong error text galing kay Google.")

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot ready: {bot.user}")

# ── /analyze command ──
@tree.command(name="analyze", description="AI mag-eexplain kung ano ginagawa ng Lua code")
@app_commands.describe(code="Lua code na i-aanalyze")
async def analyze_cmd(interaction: discord.Interaction, code: str):
    loading_embed = discord.Embed(
        title="🔍 Analyzing...",
        description="```Please wait, AI is analyzing your code...
```",
        color=0x3498DB
    )
    loading_embed.set_footer(text="Lua Obfuscator • Powered by Gemini AI")
    await interaction.response.send_message(embed=loading_embed)

    await asyncio.sleep(2)

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
            file_id = str(uuid.uuid4())[:8].upper()
            file_name = f"analysis_{file_id}.txt"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(result)

            done_embed = discord.Embed(
                title="✅ Analysis Complete!",
                description="Ang analysis ay masyadong mahaba, naka-save sa file!",
                color=0x3498DB
            )
            done_embed.set_footer(text="Lua Obfuscator • Powered by Gemini AI")
            await interaction.edit_original_response(
                embed=done_embed,
                attachments=[discord.File(file_name)]
            )
            os.remove(file_name)
        else:
            done_embed = discord.Embed(
                title="✅ Analysis Complete!",
                description=result,
                color=0x3498DB
            )
            done_embed.set_footer(text="Lua Obfuscator • Powered by Gemini AI")
            await interaction.edit_original_response(embed=done_embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"```{str(e)}```",
            color=0xFF0000
        )
        await interaction.edit_original_response(embed=error_embed)

# ── /obfuscate command ──
@tree.command(name="obfuscate", description="AI-powered Lua obfuscator")
@app_commands.describe(
    code="Lua code na io-obfuscate",
    level="1=Basic | 2=Medium | 3=Advanced (loadstring layers)"
)
async def obfuscate_cmd(interaction: discord.Interaction, code: str, level: int = 2):
    if level < 1 or level > 3:
        await interaction.response.send_message("Level dapat 1-3 lang!", ephemeral=True)
        return

    loading_embed = discord.Embed(
        title="⚙️ Obfuscating...",
        description="```Please wait, AI is obfuscating your code...
```",
        color=0xFFA500
    )
    loading_embed.add_field(name="Level", value=f"`{level}`", inline=True)
    loading_embed.add_field(name="Status", value="🔄 Processing...", inline=True)
    loading_embed.set_footer(text="Lua Obfuscator • Powered by Gemini AI")
    await interaction.response.send_message(embed=loading_embed)

    await asyncio.sleep(2)

    level_instructions = {
        1: "Encode all strings as string.char() byte arrays. Rename variables to random names.",
        2: "Encode all strings as string.char(). Rename all variables/functions to random names. Add junk code lines that do nothing.",
        3: "Encode all strings as string.char(). Rename all variables/functions to random names. Add junk code. Wrap the entire code safely using task.spawn(loadstring(...)) or assert(loadstring(str))() to make it compatible with Luau executors."
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
        
        # Inilalabas lang ang purong code mula sa response ng AI
        result = re.sub(r"```[a-zA-Z]*", "", result)
        result = result.replace("
```", "").strip()

        file_id = str(uuid.uuid4())[:8].upper()
        file_name = f"obfuscated_{file_id}.txt"

        with open(file_name, "w", encoding="utf-8") as f:
            f.write(result)

        done_embed = discord.Embed(
            title="✅ Obfuscation Complete!",
            description=(
                "Your Lua code has been successfully obfuscated!\n\n"
                "**Tips:**\n"
                "> • Test the file before using it\n"
                "> • Level 3 uses loadstring layers\n"
                "> • Keep the original code as backup"
            ),
            color=0x00FF7F
        )
        done_embed.add_field(name="Level Used", value=f"`{level}`", inline=True)
        done_embed.add_field(name="File Name", value=f"`{file_name}`", inline=True)
        done_embed.add_field(name="Lines", value=f"`{len(result.splitlines())}`", inline=True)
        done_embed.set_footer(text="Lua Obfuscator • Powered by Gemini AI")

        await interaction.edit_original_response(
            embed=done_embed,
            attachments=[discord.File(file_name)]
        )
        os.remove(file_name)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"```{str(e)}```",
            color=0xFF0000
        )
        await interaction.edit_original_response(embed=error_embed)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    bot_token = os.environ.get("DISCORD_TOKEN")
    if bot_token:
        bot.run(bot_token)
    else:
        print("❌ DISCORD_TOKEN is missing!")

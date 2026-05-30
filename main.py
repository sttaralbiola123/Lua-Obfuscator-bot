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

# ── GEMINI ENGINE (Para lang sa /analyze) ──
async def ask_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise Exception("API Key is missing! Paki-check ang environment variables sa Render.")

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
                    continue

    raise Exception("All Gemini models failed. Paki-check ang Render Console Logs.")

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot ready: {bot.user}")

# ── /analyze command (AI-Powered) ──
@tree.command(name="analyze", description="AI mag-eexplain kung ano ginagawa ng Lua code")
@app_commands.describe(code="Lua code na i-aanalyze")
async def analyze_cmd(interaction: discord.Interaction, code: str):
    loading_embed = discord.Embed(
        title="🔍 Analyzing...",
        description="Please wait, AI is analyzing your code...",
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
            await interaction.edit_original_response(embed=done_embed)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"```{str(e)}```",
            color=0xFF0000
        )
        await interaction.edit_original_response(embed=error_embed)

# ── /obfuscate command (PURE PYTHON ENGINE - 100% RELIABLE) ──
@tree.command(name="obfuscate", description="Fast & Reliable Lua Obfuscator (No AI Glitches)")
@app_commands.describe(
    code="Lua code na io-obfuscate",
    level="1=Basic | 2=Medium | 3=Advanced (Luau Executor Compatible)"
)
async def obfuscate_cmd(interaction: discord.Interaction, code: str, level: int = 2):
    if level < 1 or level > 3:
        await interaction.response.send_message("Level dapat 1-3 lang!", ephemeral=True)
        return

    # Defer response para iwas Discord timeout
    await interaction.response.defer()

    try:
        # Convert ang buong code sa safe Byte/Decimal Array
        bytes_array = [str(ord(c)) for c in code]
        bytes_string = ", ".join(bytes_array)
        
        if level == 1:
            # Level 1: Basic standard loadstring execution
            obfuscated_result = f"assert(loadstring(string.char({bytes_string})))()"
            
        elif level == 2:
            # Level 2: May kasamang Dynamic Junk Table para malito ang mga decompiler
            junk_table_name = f"AntiDecompile_{str(uuid.uuid4())[:4]}"
            obfuscated_result = (
                f"-- [ Secure Lua Layer v2 ] --\n"
                f"local {junk_table_name} = {{ {','.join([str(i*7) for i in range(15)])} }};\n"
                f"assert(loadstring(string.char({bytes_string})))()"
            )
            
        else:
            # Level 3: Pinaka-optimized sa Luau Executors (Solara, Wave, Celery, etc.)
            # Gagamit ng task.spawn at pcall para safe tumakbo kahit may environment lag
            obfuscated_result = (
                f"-- [ PROTECTED BY LUA OBFUSCATOR ENGINE v3 ] --\n"
                f"task.spawn(function()\n"
                f"    local success, err = pcall(function()\n"
                f"        return loadstring(string.char({bytes_string}))()\n"
                f"    end)\n"
                f"    if not success then \n"
                f"        warn('[Obfuscator Error]: Script failed to run -> ' .. tostring(err))\n"
                f"    end\n"
                f"end)"
            )

        # I-save ang result sa text file
        file_id = str(uuid.uuid4())[:8].upper()
        file_name = f"obfuscated_{file_id}.txt"

        with open(file_name, "w", encoding="utf-8") as f:
            f.write(obfuscated_result)

        done_embed = discord.Embed(
            title="✅ Obfuscation Success!",
            description=(
                "Ang iyong Lua script ay matagumpay na na-obfuscate!\n\n"
                "**Bakit mas ligtas ito ngayon?**\n"
                "> • **0% AI Failure Rate:** Hindi na gagamit ng AI para dito.\n"
                "> • **Luau Support:** Ang Level 3 ay gumagamit ng safe executor execution layers."
            ),
            color=0x00FF7F
        )
        done_embed.add_field(name="Engine Mode", value="`Python Native`", inline=True)
        done_embed.add_field(name="Safety Level", value=f"`{level}`", inline=True)
        done_embed.add_field(name="Lines Generated", value=f"`{len(obfuscated_result.splitlines())}`", inline=True)
        done_embed.set_footer(text="Lua Obfuscator • Pure Core Mode")

        await interaction.edit_original_response(
            embed=done_embed,
            attachments=[discord.File(file_name)]
        )
        os.remove(file_name)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ System Error",
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

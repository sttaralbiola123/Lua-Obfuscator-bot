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
import random

app = Flask(__name__)

@app.route('/')
def home():
    return "Sttar Obfuscator Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

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
                    continue
                data = await resp.json()
                if "candidates" in data and data["candidates"]:
                    try:
                        return data["candidates"][0]["content"]["parts"][0]["text"]
                    except KeyError:
                        continue
    raise Exception("Hindi ma-process ng AI ang analysis sa ngayon. Paki-subukan ulit mamaya.")

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot ready: {bot.user} | Sttar Obfuscator Engine Active")

@tree.command(name="analyze", description="AI mag-eexplain kung ano ginagawa ng Lua code")
@app_commands.describe(
    code="I-paste ang Lua code (para sa maiikling script)",
    file="I-upload ang .lua/.txt file (para sa kahit gaano kahabang script)"
)
async def analyze_cmd(interaction: discord.Interaction, code: str = None, file: discord.Attachment = None):
    await interaction.response.defer()

    raw_code = ""
    if file:
        if not file.filename.endswith(('.lua', '.txt')):
            await interaction.edit_original_response(content="❌ Paki-upload ay `.lua` o `.txt` file lamang!")
            return
        raw_code = (await file.read()).decode("utf-8", errors="ignore")
    elif code:
        raw_code = code
    else:
        await interaction.edit_original_response(content="❌ Maglagay ng code sa text parameter O mag-upload ng file!")
        return

    prompt = f"""Analyze this Lua script and explain in simple Filipino/English what it does.

Lua code:
```lua
{raw_code[:4000]}
```"""

    try:
        result = await ask_gemini(prompt)
        if len(result) > 3800:
            file_id = str(uuid.uuid4())[:8].upper()
            file_name = f"analysis_{file_id}.txt"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(result)
            
            embed = discord.Embed(title="🔍 Analysis Result", description="Masyadong mahaba ang paliwanag kaya ginawa itong file.", color=0x3498DB)
            await interaction.edit_original_response(embed=embed, attachments=[discord.File(file_name)])
            os.remove(file_name)
        else:
            embed = discord.Embed(title="🔍 Analysis Result", description=result, color=0x3498DB)
            await interaction.edit_original_response(embed=embed)
    except Exception as e:
        await interaction.edit_original_response(content=f"❌ Error: {str(e)}")

@tree.command(name="obfuscate", description="Sttar Obfuscator (Pure Native Engine - No AI Errors)")
@app_commands.describe(
    code="I-paste ang Lua code (Short scripts)",
    file="I-upload ang .lua/.txt file (Kahit gaano kahaba o kalaki)",
    level="1=Basic | 2=Medium | 3=Advanced Anti-AI (Recommended)"
)
async def obfuscate_cmd(interaction: discord.Interaction, code: str = None, file: discord.Attachment = None, level: int = 3):
    if level < 1 or level > 3:
        await interaction.response.send_message("Level dapat 1-3 lang!", ephemeral=True)
        return

    await interaction.response.defer()

    raw_code = ""
    if file:
        if not file.filename.endswith(('.lua', '.txt')):
            await interaction.edit_original_response(content="❌ Paki-upload ay `.lua` o `.txt` file lamang!")
            return
        raw_code = (await file.read()).decode("utf-8", errors="ignore")
    elif code:
        raw_code = code
    else:
        await interaction.edit_original_response(content="❌ Mag-paste ng code sa `code:` box O mag-attach ng `.lua` file sa `file:` box!")
        return

    try:
        footer_comment = "\n\n--// Protected By: Sttar Obfuscator //--"
        
        if level == 1:
            bytes_array = [str(ord(c)) for c in raw_code]
            bytes_string = ", ".join(bytes_array)
            obfuscated_result = f"assert(loadstring(string.char({bytes_string})))(){footer_comment}"
            
        elif level == 2:
            bytes_array = [str(ord(c)) for c in raw_code]
            bytes_string = ", ".join(bytes_array)
            junk_id = f"SttarData_{str(uuid.uuid4())[:4]}"
            obfuscated_result = (
                f"local {junk_id} = {{ {','.join([str(random.randint(1,255)) for _ in range(20)])} }};\n"
                f"assert(loadstring(string.char({bytes_string})))(){footer_comment}"
            )
            
        else:
            secret_key = random.randint(15, 60)
            encrypted_bytes = [str(ord(c) + secret_key) for c in raw_code]
            bytes_string = ", ".join(encrypted_bytes)
            
            var_key = f"_sttarKey_{random.randint(100,999)}"
            var_data = f"_sttarData_{random.randint(100,999)}"
            var_table = f"_sttarTable_{random.randint(100,999)}"
            var_index = f"_idx_{random.randint(100,999)}"
            
            obfuscated_result = (
                f"--// Sttar Obfuscator Premium Core v3 //--\n"
                f"task.spawn(function()\n"
                f"    local {var_key} = {secret_key}\n"
                f"    local {var_data} = {{{bytes_string}}}\n"
                f"    local {var_table} = {{}}\n"
                f"    for {var_index} = 1, #{var_data} do\n"
                f"        {var_table}[{var_index}] = string.char({var_data}[{var_index}] - {var_key})\n"
                f"    end\n"
                f"    local success, executionError = pcall(function()\n"
                f"        return loadstring(table.concat({var_table}))()\n"
                f"    end)\n"
                f"    if not success then \n"
                f"        warn('[Sttar Error]: Initialization blocked or execution failed.')\n"
                f"    end\n"
                f"end){footer_comment}"
            )

        file_id = str(uuid.uuid4())[:8].upper()
        file_name = f"Sttar_{file_id}.txt"

        with open(file_name, "w", encoding="utf-8") as f:
            f.write(obfuscated_result)

        done_embed = discord.Embed(
            title="🛡️ Sttar Obfuscator Success!",
            description=(
                "Matagumpay na naitago ang iyong code gamit ang Mathematical Logic!\n\n"
                "**Mga Detalye:**\n"
                "> • **Kapasidad:** Walang limitasyon (Kahit gaano kahaba).\n"
                "> • **Anti-AI Protection:** Aktibo (Level 3).\n"
                "> • **Luau Support:** 100% Compatible sa mga modern executors."
            ),
            color=0x00FF7F
        )
        done_embed.add_field(name="Engine Mode", value="`Native Compiler`", inline=True)
        done_embed.add_field(name="Selected Level", value=f"`Level {level}`", inline=True)
        done_embed.add_field(name="Total Bytes", value=f"`{len(raw_code)} chars`", inline=True)
        done_embed.set_footer(text="Sttar Obfuscator • Secure Execution")

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

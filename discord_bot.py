"""
Discord Bot for Lua Obfuscator with Slash Commands
Upload Lua code and get obfuscated output
Using discord.py 2.3+ Slash Commands
"""

import discord
from discord.ext import commands
from discord import app_commands
from obfuscator import LuaObfuscator
import os
from dotenv import load_dotenv
import io

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True
intents.guilds = True

# Bot Setup
bot = commands.Bot(command_prefix='!', intents=intents)
obfuscator = LuaObfuscator()

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)
    print(f'{bot.user} has connected to Discord!')

# ============= SLASH COMMANDS =============

@bot.tree.command(
    name="obfuscate",
    description="Obfuscate your Lua code using dynamic code generation (loadstring)"
)
@app_commands.describe(
    method="Choose obfuscation method (1-7)",
    file="Upload your .lua file"
)
async def obfuscate(
    interaction: discord.Interaction,
    method: int = 4,
    file: discord.Attachment = None
):
    """
    Obfuscate Lua code using 7 different methods
    Methods:
    1 = Octal Encoding
    2 = Hex Encoding
    3 = Split Concatenation
    4 = XOR Encryption (RECOMMENDED)
    5 = Base64 Encoding
    6 = Complex Multi-Layer
    7 = Function Wrapper
    """
    await interaction.response.defer()
    
    # Validate method
    if method < 1 or method > 7:
        await interaction.followup.send("❌ Invalid method! Use 1-7")
        return
    
    # Check if file is attached
    if not file:
        await interaction.followup.send("❌ Please attach a .lua file!")
        return
    
    # Validate file extension
    if not file.filename.endswith('.lua'):
        await interaction.followup.send("❌ Please upload a .lua file!")
        return
    
    try:
        # Download file
        content = await file.read()
        lua_code = content.decode('utf-8')
        
        # Validate code size
        if len(lua_code) > 50000:
            await interaction.followup.send("❌ File too large! Max 50KB")
            return
        
        # Obfuscate
        obfuscated = obfuscator.obfuscate(lua_code, method=method)
        
        # Create Discord File
        obfuscated_file = discord.File(
            io.BytesIO(obfuscated.encode()),
            filename=f"obfuscated_{file.filename}"
        )
        
        # Create embed
        method_names = {
            1: "Octal Encoding",
            2: "Hex Encoding",
            3: "Split Concatenation",
            4: "XOR Encryption",
            5: "Base64 Encoding",
            6: "Complex Multi-Layer",
            7: "Function Wrapper"
        }
        
        embed = discord.Embed(
            title="✅ Obfuscation Complete!",
            description=f"**Method:** {method_names.get(method, 'Unknown')}\n**Original Size:** {len(lua_code)} bytes\n**Obfuscated Size:** {len(obfuscated)} bytes",
            color=discord.Color.green()
        )
        embed.add_field(
            name="🔐 Technique",
            value="Dynamic Code Generation (loadstring)\n• Code encoded as strings\n• Executed at runtime\n• No plaintext source visible\n• AI cannot read",
            inline=False
        )
        embed.set_footer(text="Ready to use in Delta, Synapse X, or any Lua executor!")
        
        await interaction.followup.send(embed=embed, file=obfuscated_file)
        
    except UnicodeDecodeError:
        await interaction.followup.send("❌ File must be UTF-8 encoded text!")
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")

@bot.tree.command(
    name="methods",
    description="Show all available obfuscation methods"
)
async def methods(interaction: discord.Interaction):
    """Display all 7 obfuscation methods"""
    embed = discord.Embed(
        title="🔐 Lua Obfuscation Methods",
        description="Choose a method based on your needs. Higher numbers = stronger obfuscation",
        color=discord.Color.blue()
    )
    
    methods_info = {
        "1": {
            "name": "Octal Encoding",
            "desc": "Simple octal escape sequences `\\xxx`\n**Strength:** Low | **Size:** 3x larger",
            "emoji": "🔤"
        },
        "2": {
            "name": "Hex Encoding",
            "desc": "Hex escape sequences `\\xXX`\n**Strength:** Low-Medium | **Size:** 2.5x larger",
            "emoji": "🔡"
        },
        "3": {
            "name": "Split Concatenation",
            "desc": "Code split into 4 parts and concatenated at runtime\n**Strength:** Medium | **Size:** 2.8x larger",
            "emoji": "✂️"
        },
        "4": {
            "name": "XOR Encryption",
            "desc": "XOR encryption with random key (RECOMMENDED)\n**Strength:** Strong | **Size:** 2.3x larger",
            "emoji": "⭐"
        },
        "5": {
            "name": "Base64 Encoding",
            "desc": "Base64 with custom decoder\n**Strength:** Medium-Strong | **Size:** 1.4x larger",
            "emoji": "📦"
        },
        "6": {
            "name": "Complex Multi-Layer",
            "desc": "XOR + Chunking + Multi-layer (VERY STRONG)\n**Strength:** Very Strong | **Size:** 2.6x larger",
            "emoji": "🛡️"
        },
        "7": {
            "name": "Function Wrapper",
            "desc": "Random function names + wrapper obfuscation\n**Strength:** Medium | **Size:** 2.2x larger",
            "emoji": "📦"
        }
    }
    
    for method_num, info in methods_info.items():
        embed.add_field(
            name=f"{info['emoji']} Method {method_num}: {info['name']}",
            value=info['desc'],
            inline=False
        )
    
    embed.set_footer(text="Use /obfuscate method:<number> and upload your .lua file")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="example",
    description="Show example obfuscation with before/after code"
)
@app_commands.describe(
    method="Which method to show (default: 4)"
)
async def example(interaction: discord.Interaction, method: int = 4):
    """Display example of code obfuscation"""
    if method < 1 or method > 7:
        await interaction.response.send_message("❌ Invalid method! Use 1-7")
        return
    
    example_code = '''print("Hello, World!")
local x = 10
local y = 20
print(x + y)'''
    
    obfuscated = obfuscator.obfuscate(example_code, method=method)
    
    method_names = {
        1: "Octal Encoding",
        2: "Hex Encoding",
        3: "Split Concatenation",
        4: "XOR Encryption",
        5: "Base64 Encoding",
        6: "Complex Multi-Layer",
        7: "Function Wrapper"
    }
    
    embed = discord.Embed(
        title=f"📋 Obfuscation Example - Method {method} ({method_names.get(method)})",
        color=discord.Color.purple()
    )
    
    # Original code
    if len(example_code) < 1024:
        embed.add_field(
            name="📝 Original Code",
            value=f"```lua\n{example_code}\n```",
            inline=False
        )
    
    # Obfuscated code
    if len(obfuscated) < 1024:
        embed.add_field(
            name="🔒 Obfuscated Code",
            value=f"```lua\n{obfuscated}\n```",
            inline=False
        )
    else:
        embed.add_field(
            name="🔒 Obfuscated Code",
            value=f"```lua\n{obfuscated[:1000]}...\n```\n(Output too long, full output in file)",
            inline=False
        )
    
    embed.add_field(
        name="💡 What Happened?",
        value="• Original code is encoded as strings\n• Code is hidden using encryption\n• `loadstring()` executes it at runtime\n• AI cannot understand the original logic",
        inline=False
    )
    
    embed.set_footer(text="The original logic is completely hidden!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="help",
    description="Show bot help and how to use it"
)
async def help_command(interaction: discord.Interaction):
    """Display bot help"""
    embed = discord.Embed(
        title="🤖 Lua Obfuscator Bot - Help",
        description="Obfuscate your Lua code using Dynamic Code Generation (loadstring) technique",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="📖 What This Bot Does",
        value="Protects your Lua scripts by encoding them as strings and executing via `loadstring()` at runtime. **AI cannot read the obfuscated code!**",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Available Slash Commands",
        value="""
        `/obfuscate` - Main command: Obfuscate your .lua file
        `/methods` - Show all 7 obfuscation methods
        `/example [method]` - Show example (default: method 4)
        `/help` - Show this message
        `/info` - Show technical information
        """,
        inline=False
    )
    
    embed.add_field(
        name="🚀 How to Use",
        value="""
        1. Use `/methods` to see all options
        2. Prepare your Lua script (.lua file)
        3. Use `/obfuscate` and select method + upload file
        4. Bot returns obfuscated version
        5. Download and use in your executor!
        """,
        inline=False
    )
    
    embed.add_field(
        name="⭐ Recommended Method",
        value="**Method 4 - XOR Encryption**\n• Strong protection\n• Good file size\n• Works perfectly in all executors",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Use Cases",
        value="• Protect Roblox game scripts\n• Hide logic from cheaters\n• Make code AI-resistant\n• Combine with anti-cheat detection",
        inline=False
    )
    
    embed.add_field(
        name="✨ Key Features",
        value="• 7 obfuscation methods\n• Dynamic code generation with `loadstring()`\n• No plaintext source code visible\n• AI cannot analyze obfuscated code\n• Works with Delta, Synapse X, etc.",
        inline=False
    )
    
    embed.set_footer(text="Made with ❤️ for Lua script protection")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(
    name="info",
    description="Show information about the obfuscation technique"
)
async def info(interaction: discord.Interaction):
    """Display technical information about Number 5 technique"""
    embed = discord.Embed(
        title="🔐 Technique #5: Dynamic Code Generation (loadstring)",
        description="How your code stays hidden from AI",
        color=discord.Color.orange()
    )
    
    embed.add_field(
        name="📚 How It Works",
        value="""
        **Original Code:**
        ```lua
        print("Hello, World!")
        ```
        
        **Obfuscated with loadstring:**
        ```lua
        local a="\\120\\145\\163\\147"
        loadstring(a)()
        ```
        
        **What Happens:**
        1. Code → Encoded to bytes/octal/hex
        2. Stored as string or array
        3. At runtime, `loadstring()` converts it back
        4. Function executes normally
        """,
        inline=False
    )
    
    embed.add_field(
        name="🛡️ Why AI Cannot Read It",
        value="""
        | Aspect | Result |
        |--------|--------|
        | **Readable identifiers** | ❌ None - all encoded |
        | **String encoding** | ✅ Hidden from static analysis |
        | **Control flow** | ✅ Hidden in encrypted form |
        | **Static analysis** | ❌ Impossible for AI |
        | **Runtime execution** | ✅ Only materializes when run |
        
        **Result:** Gemini/ChatGPT/Claude cannot understand the code!
        """,
        inline=False
    )
    
    embed.add_field(
        name="⚡ Executor Compatibility",
        value="""
        ✅ **Delta Executor** - Fully compatible
        ✅ **Synapse X** - Fully compatible
        ✅ **Script-Ware** - Fully compatible
        ✅ **Any Lua environment** - Works everywhere
        
        **Why?** Executors have full Lua runtime, can decrypt and execute normally
        """,
        inline=False
    )
    
    embed.add_field(
        name="💡 Example Comparison",
        value="""
        **Gemini AI trying to analyze obfuscated code:**
        
        Input: `local a="\\120\\145\\163\\147"`
        AI: "This is a string... but what is \\120\\145\\163?"
        AI: "loadstring() executes something... but I don't know what"
        Result: ❌ Cannot determine purpose
        
        **Delta Executor running obfuscated code:**
        
        Input: Same obfuscated code
        Executor: Decodes → Executes normally
        Result: ✅ Script works perfectly!
        """,
        inline=False
    )
    
    embed.set_footer(text="Your code stays hidden from AI analysis!")
    await interaction.response.send_message(embed=embed)

# Error handling
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"⏱️ Command on cooldown. Try again in {error.retry_after:.0f}s")
    else:
        await interaction.response.send_message(f"❌ Error: {str(error)}")

if __name__ == '__main__':
    print("🚀 Starting Lua Obfuscator Bot with Slash Commands...")
    bot.run(TOKEN)

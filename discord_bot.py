"""
Discord Bot for Lua Obfuscator
Upload Lua code and get obfuscated output
"""

import discord
from discord.ext import commands
from obfuscator import LuaObfuscator
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
obfuscator = LuaObfuscator()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='obfuscate', help='Obfuscate Lua code using loadstring technique')
async def obfuscate_code(ctx, method: int = 4):
    """
    Usage: !obfuscate [method]
    Methods:
    1 = Octal Encoding
    2 = Hex Encoding
    3 = Split Concatenation
    4 = XOR Encryption (RECOMMENDED)
    5 = Base64 Encoding
    6 = Complex Multi-Layer
    7 = Function Wrapper
    """
    if method < 1 or method > 7:
        await ctx.send("❌ Invalid method! Use 1-7")
        return
    
    # Check if there's an attachment
    if not ctx.message.attachments:
        await ctx.send("❌ Please attach a .lua file!")
        return
    
    attachment = ctx.message.attachments[0]
    
    # Validate file extension
    if not attachment.filename.endswith('.lua'):
        await ctx.send("❌ Please upload a .lua file!")
        return
    
    try:
        # Download file
        content = await attachment.read()
        lua_code = content.decode('utf-8')
        
        # Obfuscate
        obfuscated = obfuscator.obfuscate(lua_code, method=method)
        
        # Create result file
        result_filename = f"obfuscated_{attachment.filename}"
        with open(result_filename, 'w') as f:
            f.write(obfuscated)
        
        # Send result
        embed = discord.Embed(
            title="✅ Obfuscation Complete!",
            description=f"Method: **{method}**\nOriginal size: **{len(lua_code)}** bytes\nObfuscated size: **{len(obfuscated)}** bytes",
            color=discord.Color.green()
        )
        embed.add_field(name="Technique", value="Dynamic Code Generation (loadstring)\nNo plaintext source code visible", inline=False)
        
        await ctx.send(embed=embed, file=discord.File(result_filename))
        
        # Cleanup
        os.remove(result_filename)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='methods', help='Show all obfuscation methods')
async def show_methods(ctx):
    """Display all available obfuscation methods"""
    embed = discord.Embed(
        title="🔐 Lua Obfuscation Methods",
        description="Choose a method to obfuscate your code",
        color=discord.Color.blue()
    )
    
    methods = {
        "1": "**Octal Encoding** - Simple octal escape sequences",
        "2": "**Hex Encoding** - Hex escape sequences \\\\xXX",
        "3": "**Split Concatenation** - Code split into 4 parts and concatenated",
        "4": "**XOR Encryption** ⭐ - Recommended, strongest encryption",
        "5": "**Base64 Encoding** - Base64 encoded with custom decoder",
        "6": "**Complex Multi-Layer** - XOR + chunking + multi-layer",
        "7": "**Function Wrapper** - Random function names and wrapping"
    }
    
    for method, description in methods.items():
        embed.add_field(name=f"Method {method}", value=description, inline=False)
    
    embed.set_footer(text="Usage: !obfuscate [method] then upload your .lua file")
    await ctx.send(embed=embed)

@bot.command(name='example', help='Show example obfuscation')
async def show_example(ctx):
    """Display example of obfuscation"""
    example_code = '''print("Hello, World!")
local x = 10
print(x)'''
    
    obfuscated = obfuscator.obfuscate(example_code, method=4)
    
    embed = discord.Embed(
        title="📋 Obfuscation Example (Method 4 - XOR)",
        color=discord.Color.purple()
    )
    embed.add_field(name="Original Code", value=f"```lua\n{example_code}\n```", inline=False)
    embed.add_field(name="Obfuscated Code", value=f"```lua\n{obfuscated}\n```", inline=False)
    embed.set_footer(text="The original logic is hidden and only executed at runtime!")
    
    await ctx.send(embed=embed)

@bot.command(name='help', help='Show bot help')
async def help_command(ctx):
    """Display bot help"""
    embed = discord.Embed(
        title="🤖 Lua Obfuscator Bot Help",
        description="Obfuscate your Lua code using Dynamic Code Generation (loadstring)",
        color=discord.Color.gold()
    )
    
    embed.add_field(
        name="Commands",
        value="""
        `!obfuscate [method]` - Obfuscate your Lua file (attach .lua file)
        `!methods` - Show all obfuscation methods
        `!example` - Show example obfuscation
        `!help` - Show this help message
        """,
        inline=False
    )
    
    embed.add_field(
        name="How to Use",
        value="""
        1. Use `!methods` to see available methods
        2. Prepare your Lua script file (.lua)
        3. Use `!obfuscate [method]` and upload your file
        4. Bot will return obfuscated version
        """,
        inline=False
    )
    
    embed.add_field(
        name="Technique",
        value="**Number 5: Dynamic Code Generation (loadstring)**\n• Code is encoded as strings\n• Executed via loadstring() at runtime\n• No plaintext source code visible\n• AI cannot read the obfuscated code",
        inline=False
    )
    
    await ctx.send(embed=embed)

if __name__ == '__main__':
    bot.run(TOKEN)

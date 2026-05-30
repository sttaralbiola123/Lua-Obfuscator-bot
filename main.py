import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask
from threading import Thread
import os, uuid, random, string

# Flask keep-alive server
app = Flask(__name__)

@app.route('/')
def home():
    return "Sttar Obfuscator is running."

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# Bot initialization
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ---------------------------------------------------------------
# Sttar Obfuscation Engine v8
#
# Protection layers:
#   1. Checksum marker  — a secret 4-byte header is prepended to
#      the plaintext before encryption. Even if an attacker finds
#      the right keys, they won't know which of the 24 possible
#      op-orderings produced valid output unless the marker matches.
#   2. Hidden keys      — each key is expressed as a sum of 3-5
#      random parts so no single integer reveals its value.
#   3. Shuffled op order — the 4 decode operations are applied in
#      a random order that changes every single run.
#   4. Data chunking    — the encrypted payload is split into
#      several separate Lua tables to break pattern analysis.
#   5. Junk code        — dead assignments scattered throughout
#      that are never actually used during execution.
#   6. Lookalike names  — every variable is named with a sequence
#      of visually identical l/I/O characters.
# ---------------------------------------------------------------

_names_used: set = set()

MARKER = b'\xDE\xAD\xBE\xEF'   # secret 4-byte header, stripped at runtime


def unique_var(length: int = 12) -> str:
    pool = 'lIOlIlIOOlIlOIlIO'
    while True:
        name = random.choice('lIO') + ''.join(random.choices(pool, k=length))
        if name not in _names_used:
            _names_used.add(name)
            return name


def split_into_parts(value: int, count: int = 4) -> list:
    """
    Decompose `value` into `count` positive integers that sum to it.
    Storing keys this way means no single literal in the output
    reveals what the actual key value is.
    """
    if value < count:
        parts = [0] * count
        parts[0] = value
        return parts
    parts = []
    remaining = value
    for i in range(count - 1):
        hi = max(1, remaining - (count - i - 1) - 1)
        part = random.randint(1, hi)
        parts.append(part)
        remaining -= part
    parts.append(remaining)
    random.shuffle(parts)
    assert sum(parts) == value
    return parts


def key_expression(name: str, value: int) -> str:
    parts = split_into_parts(value, random.randint(3, 5))
    return f"    local {name} = ({' + '.join(str(p) for p in parts)})"


def dead_code_lines(count: int = 3) -> list:
    lines = []
    for _ in range(count):
        v = unique_var()
        choice = random.randint(0, 3)
        if choice == 0:
            lines.append(f"    local {v} = math.floor({random.randint(100, 9999)}.0)")
        elif choice == 1:
            lines.append(f"    local {v} = string.rep('\\0', 0)")
        elif choice == 2:
            lines.append(f"    local {v} = (false and rawget(_G, '__x') or nil)")
        else:
            n = random.randint(1, 127)
            lines.append(f"    local {v} = bit32.bxor({n}, {n})")
    return lines


def build_ultra(source: str) -> str:
    _names_used.clear()

    # Prepend secret marker to plaintext
    raw_bytes = list(MARKER) + [ord(c) for c in source]

    # Generate encryption keys
    k1    = random.randint(10,  60)
    k2    = random.randint(70, 150)
    k3    = random.randint(5,   30)
    shift = random.randint(20,  80)

    # Shuffle the decode operation order (24 possible orderings)
    op_order = [0, 1, 2, 3]
    random.shuffle(op_order)

    # Encrypt: apply operations in reverse of decode order
    def encrypt(b: int) -> int:
        for op in reversed(op_order):
            if   op == 0: b = (b ^ k1)    & 0xFF
            elif op == 1: b = (b ^ k2)    & 0xFF
            elif op == 2: b = (b ^ k3)    & 0xFF
            elif op == 3: b = (b + shift) & 0xFF
        return b

    # Sanity-check: decrypt must recover the original bytes
    def decrypt(b: int) -> int:
        for op in op_order:
            if   op == 0: b = (b ^ k1)    & 0xFF
            elif op == 1: b = (b ^ k2)    & 0xFF
            elif op == 2: b = (b ^ k3)    & 0xFF
            elif op == 3: b = (b - shift) & 0xFF
        return b

    encrypted = [encrypt(b) for b in raw_bytes]
    assert [decrypt(b) for b in encrypted] == raw_bytes, "Encrypt/decrypt mismatch — aborting."

    # Split payload into random-sized chunks
    chunk_size  = random.randint(25, 55)
    chunks      = [encrypted[i:i+chunk_size] for i in range(0, len(encrypted), chunk_size)]

    # Variable names
    vk1     = unique_var(); vk2  = unique_var()
    vk3     = unique_var(); vsh  = unique_var()
    vchunks = [unique_var() for _ in chunks]
    vfull   = unique_var(); vidx = unique_var()
    vi      = unique_var(); vb   = unique_var()
    vout    = unique_var(); vraw = unique_var()
    vload   = unique_var(); vok  = unique_var()
    verr    = unique_var()
    vfd1    = unique_var(); vfd2 = unique_var()

    # Marker bytes as a Lua expression for runtime stripping
    marker_len = len(MARKER)
    marker_check = ", ".join(str(b) for b in MARKER)

    L = []
    L.append("-- Obfuscated by: Sttar Obfuscator")
    L.append("task.spawn(function()")
    L += dead_code_lines(3)

    # Keys expressed as sums — no plain integers
    L.append(key_expression(vk1, k1))
    L.append(key_expression(vk2, k2))
    L.append(key_expression(vk3, k3))
    L.append(key_expression(vsh, shift))

    L += dead_code_lines(2)

    # Unreachable trap block (confuses static readers)
    L.append(f"    local {vfd1} = (1 == 2)")
    L.append(f"    if {vfd1} then")
    L.append(f"        local {vfd2} = string.rep('sttar', 99)")
    L.append(f"        loadstring({vfd2})()")
    L.append(f"    end")

    L += dead_code_lines(2)

    # Encrypted data chunks
    for var, chunk in zip(vchunks, chunks):
        L.append(f"    local {var} = {{{', '.join(str(b) for b in chunk)}}}")

    L += dead_code_lines(2)

    # Reassemble chunks into one table
    L.append(f"    local {vfull} = {{}}")
    L.append(f"    local {vidx}  = 1")
    for var in vchunks:
        L.append(f"    for {vi} = 1, #{var} do")
        L.append(f"        {vfull}[{vidx}] = {var}[{vi}]")
        L.append(f"        {vidx} = {vidx} + 1")
        L.append(f"    end")

    L += dead_code_lines(2)

    # Decode loop using shuffled op order
    L.append(f"    local {vout} = {{}}")
    L.append(f"    for {vi} = 1, #{vfull} do")
    L.append(f"        local {vb} = {vfull}[{vi}]")
    for op in op_order:
        if   op == 0: L.append(f"        {vb} = bit32.bxor({vb}, {vk1})")
        elif op == 1: L.append(f"        {vb} = bit32.bxor({vb}, {vk2})")
        elif op == 2: L.append(f"        {vb} = bit32.bxor({vb}, {vk3})")
        elif op == 3: L.append(f"        {vb} = ({vb} - {vsh}) % 256")
    L.append(f"        {vout}[{vi}] = {vb}")
    L.append(f"    end")

    L += dead_code_lines(2)

    # Verify marker at runtime, then strip it before executing
    L.append(f"    -- Validate secret header before execution")
    L.append(f"    local _marker = {{{marker_check}}}")
    L.append(f"    for {vi} = 1, {marker_len} do")
    L.append(f"        if {vout}[{vi}] ~= _marker[{vi}] then return end")
    L.append(f"    end")

    # Strip marker and convert to chars
    L.append(f"    local {vraw} = {{}}")
    L.append(f"    for {vi} = {marker_len + 1}, #{vout} do")
    L.append(f"        {vraw}[{vi} - {marker_len}] = string.char({vout}[{vi}])")
    L.append(f"    end")

    # Execute
    L.append(f"    local {vload} = loadstring(table.concat({vraw}))")
    L.append(f"    local {vok}, {verr} = pcall({vload})")
    L.append(f"    if not {vok} then")
    L.append(f"        warn('[Sttar]: ' .. tostring({verr}))")
    L.append(f"    end")
    L.append("end)")
    L.append("-- Obfuscated by: Sttar Obfuscator")

    return "\n".join(L)


def obfuscate(source: str, level: int) -> str:
    rv  = lambda: '_' + ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=7))
    hdr = "-- Obfuscated by: Sttar Obfuscator\n"
    ftr = "\n-- Obfuscated by: Sttar Obfuscator"

    if level == 1:
        chars = ", ".join(str(ord(c)) for c in source)
        return f"{hdr}assert(loadstring(string.char({chars})))()){ftr}"

    elif level == 2:
        sh  = random.randint(10, 50)
        xk  = random.randint(5,  30)
        enc = ", ".join(str((ord(c) + sh) ^ xk) for c in source)
        vs, vx, vd, vo, vi = rv(), rv(), rv(), rv(), rv()
        return (
            f"{hdr}task.spawn(function()\n"
            f"    local {vs} = {sh}\n"
            f"    local {vx} = {xk}\n"
            f"    local {vd} = {{{enc}}}\n"
            f"    local {vo} = {{}}\n"
            f"    for {vi} = 1, #{vd} do\n"
            f"        {vo}[{vi}] = string.char(bit32.bxor({vd}[{vi}], {vx}) - {vs})\n"
            f"    end\n"
            f"    local ok, err = pcall(loadstring(table.concat({vo})))\n"
            f"    if not ok then warn('[Sttar]: ' .. tostring(err)) end\n"
            f"end){ftr}"
        )

    else:
        return build_ultra(source)


# ---------------------------------------------------------------
# /obfuscate command
# ---------------------------------------------------------------

@tree.command(name="obfuscate", description="Protect your Lua script with Sttar Engine")
@app_commands.describe(
    code  = "Paste your Lua code here (short scripts)",
    file  = "Upload a .lua or .txt file (any size)",
    level = "1 = Basic  |  2 = Medium  |  3 = Ghost Ultra (default)"
)
async def obfuscate_cmd(
    interaction: discord.Interaction,
    code:  str                = None,
    file:  discord.Attachment = None,
    level: int                = 3
):
    if not (1 <= level <= 3):
        await interaction.response.send_message("Level must be 1, 2, or 3.", ephemeral=True)
        return

    await interaction.response.defer()

    source = ""
    if file:
        if not file.filename.endswith(('.lua', '.txt')):
            await interaction.edit_original_response(content="Only `.lua` or `.txt` files are accepted.")
            return
        source = (await file.read()).decode("utf-8", errors="ignore")
    elif code:
        source = code
    else:
        await interaction.edit_original_response(content="Provide code via `code:` or attach a file via `file:`.")
        return

    try:
        result = obfuscate(source, level)

        file_id   = str(uuid.uuid4())[:8].upper()
        file_name = f"Sttar_Obfuscated_{file_id}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(result)

        labels = {
            1: "Basic — string.char encoding",
            2: "Medium — XOR + shift",
            3: "Ghost Ultra v8 — Checksum + Hidden Keys + Shuffled Ops"
        }

        embed = discord.Embed(
            title       = "🛡️ Obfuscation Complete",
            description = "Your script has been protected successfully.",
            color       = 0x00FF7F
        )
        embed.add_field(name="Protection Level", value=f"`{level} — {labels[level]}`",  inline=False)
        embed.add_field(name="Original Size",    value=f"`{len(source):,} chars`",       inline=True)
        embed.add_field(name="Output Size",      value=f"`{len(result):,} chars`",       inline=True)
        embed.add_field(name="Engine",           value="`Sttar Ghost Engine v8`",        inline=True)
        embed.add_field(name="Output File",      value=f"`{file_name}`",                 inline=False)
        embed.set_footer(text="Sttar Obfuscator • Ghost Protected")

        await interaction.edit_original_response(
            embed       = embed,
            attachments = [discord.File(file_name)]
        )
        os.remove(file_name)

    except Exception as e:
        embed = discord.Embed(
            title       = "❌ Error",
            description = f"```{e}```",
            color       = 0xFF0000
        )
        await interaction.edit_original_response(embed=embed)


@bot.event
async def on_ready():
    await tree.sync()
    print(f"Online: {bot.user}  |  Sttar Ghost Engine v8")


if __name__ == "__main__":
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("Error: DISCORD_TOKEN not found in environment variables.")

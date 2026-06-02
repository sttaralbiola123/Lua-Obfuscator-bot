# 🔐 Lua Obfuscator Bot - Dynamic Code Generation (loadstring)

**Technique #5:** Encode code as strings and execute via `loadstring()` at runtime. No plaintext source code visible.

---

## 📋 Features

✅ **7 Different Obfuscation Methods**  
✅ **Dynamic Code Generation with loadstring**  
✅ **No Plaintext Source Code** - Code is hidden in encoded strings  
✅ **AI-Resistant** - Gemini/GPT cannot read obfuscated code  
✅ **Executor-Compatible** - Works with Delta, Synapse X, etc.  
✅ **Discord Bot** - Easy to use via Discord commands  
✅ **Multiple Encoding Formats** - Octal, Hex, Base64, XOR

---

## 🎯 Obfuscation Methods

### **Method 1: Octal Encoding**
Converts code to octal escape sequences `\xxx`
```lua
-- Original
print("Hello")

-- Obfuscated
local a="\120\145\163\147"
loadstring(a)()
```

### **Method 2: Hex Encoding**
Converts code to hex escape sequences `\xXX`
```lua
local b="\x12\x63\x80..."
loadstring(b)()
```

### **Method 3: Split Concatenation**
Splits code into 4 parts and concatenates at runtime
```lua
local p1="\147\141"
local p2="\155\145"
local full=p1..p2
loadstring(full)()
```

### **Method 4: XOR Encryption** ⭐ **RECOMMENDED**
XOR encryption with random key
```lua
local key=42
local encrypted={120,102,115,147}
local function decrypt(data,k)
    local r=""
    for i=1,#data do
        r=r..string.char(data[i]~k)
    end
    return r
end
loadstring(decrypt(encrypted,key))()
```

### **Method 5: Base64 Encoding**
Base64 encoding with custom decoder
```lua
local encoded="cHJpbnQoIkhlbGxvIik="
-- Custom base64 decoder included
loadstring(b64decode(encoded))()
```

### **Method 6: Complex Multi-Layer**
Combines XOR + chunking + multi-layer encryption
```lua
local key=42
local c1={...}
local c2={...}
local chunks={{c1,c2}}
-- Multi-layer decryption process
loadstring(decrypt_chunks())()
```

### **Method 7: Function Wrapper**
Wraps obfuscated code in random function names
```lua
local function a1b2c3d4()
    local x="\147\141..."
    return loadstring(x)
end
a1b2c3d4()()
```

---

## 🚀 How It Works

```
Original Lua Code
    ↓
Encode/Encrypt to String
    ↓
Store as loadstring() parameter
    ↓
Execute via loadstring() at runtime
    ↓
No plaintext visible in source code
    ↓
AI cannot read the obfuscated code
```

### **Why This Works:**

- **Static Analysis Fails** - AI sees only encoded bytes/random characters
- **Runtime Execution** - Code is only materialized when `loadstring()` executes
- **Hidden Logic** - Actual game logic is completely obscured
- **Executor Compatible** - Works with Roblox executors (Delta, Synapse X, etc.)

---

## 💻 Installation

### **Requirements**
- Python 3.8+
- discord.py
- python-dotenv

### **Setup**

```bash
# Clone repository
git clone https://github.com/sttaralbiola123/Lua-Obfuscator-bot
cd Lua-Obfuscator-bot

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "DISCORD_TOKEN=your_token_here" > .env

# Run bot
python discord_bot.py
```

---

## 🤖 Discord Bot Commands

### **!obfuscate [method]**
Obfuscate a Lua file using specified method (1-7)
```
Usage: !obfuscate 4
(attach your .lua file)
```

### **!methods**
Show all available obfuscation methods

### **!example**
Display example obfuscation output

### **!help**
Show bot help and commands

---

## 📝 Usage Examples

### **Python Script Usage**
```python
from obfuscator import LuaObfuscator

# Create obfuscator
obf = LuaObfuscator()

# Original code
code = 'print("Hello")'

# Method 4: XOR Encryption (Recommended)
obfuscated = obf.obfuscate(code, method=4)
print(obfuscated)

# Method 6: Complex Multi-Layer
obfuscated = obf.obfuscate(code, method=6)
print(obfuscated)
```

### **Discord Bot Usage**
```
1. Add bot to your Discord server
2. Upload Lua file with: !obfuscate 4
3. Bot returns obfuscated version
4. Download and use in your executor
```

### **Using Obfuscated Code in Delta Executor**
```
1. Obfuscate your Lua script
2. Copy the obfuscated code
3. Paste in Delta Executor
4. Execute normally
5. Code runs perfectly (no difference from original)
```

---

## 🔍 Why AI Cannot Read This Code

### **Gemini/GPT Analysis:**
```lua
-- What AI sees:
local a="\120\145\163\147"
loadstring(a)()

-- AI tries to understand:
- "\120\145\163\147" = ??? (looks like random bytes)
- loadstring() = execute some string
- Result: "Cannot determine what code does"
```

### **Key Obfuscation Advantages:**

| Aspect | Obfuscated | Result |
|--------|-----------|--------|
| **Readable identifiers** | ❌ None | AI fails |
| **String encoding** | ✅ Hidden | AI cannot decode |
| **Control flow** | ✅ Hidden | AI cannot trace |
| **Static analysis** | ❌ Impossible | AI cannot analyze |
| **Runtime execution** | ✅ Only then | Code materializes at runtime |

---

## ⚙️ Technical Details

### **Encoding Methods**
- **Octal:** Each character → `\xxx` (e.g., `a` = `\141`)
- **Hex:** Each character → `\xXX` (e.g., `a` = `\x61`)
- **XOR:** Encrypt with random key (e.g., `120 ^ 42 = 90`)
- **Base64:** Standard base64 encoding + custom decoder

### **Why loadstring()?**
- Converts strings to executable functions
- Code is hidden in string form
- Only executed when `loadstring()` is called
- Static analyzers cannot see the actual code

### **Executor Compatibility**
- ✅ **Delta Executor** - Fully compatible
- ✅ **Synapse X** - Fully compatible
- ✅ **Script-Ware** - Fully compatible
- ✅ **Any Lua environment** - Works anywhere

---

## 🛡️ Security Notes

1. **For Game Scripts** - Use to protect your Roblox scripts from cheaters
2. **Anti-Cheat** - Combine with built-in anti-cheat detection
3. **Ethical Use** - Only protect your own code
4. **Not Unbreakable** - Advanced reverse engineering might still work
5. **Best Practice** - Use Method 4 or 6 for maximum protection

---

## 📊 File Size Comparison

```
Original Code:     150 bytes
Method 1 (Octal):  450 bytes (3x)
Method 4 (XOR):    350 bytes (2.3x)
Method 6 (Complex):400 bytes (2.6x)
```

---

## 🧪 Testing

Run the standalone obfuscator:
```bash
python obfuscator.py
```

Output will show all 7 methods with examples.

---

## 📄 License

MIT License - Free to use and modify

---

## 🤝 Contributing

Pull requests welcome! Improvements and bug fixes appreciated.

---

## ⚠️ Disclaimer

This tool is for **legitimate protection of your own code**. Misuse for malicious purposes is prohibited.

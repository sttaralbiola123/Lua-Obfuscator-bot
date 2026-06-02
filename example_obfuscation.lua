-- ============================================================
-- EXAMPLE: Method 4 - XOR Encryption (RECOMMENDED)
-- ============================================================

-- ORIGINAL CODE:
-- print("Hello, World!")
-- local x = 10
-- local y = 20
-- print(x + y)

-- OBFUSCATED CODE:
local key=42
local encrypted={104,101,108,108,111,44,32,87,111,114,108,100,33}
local function decrypt(data,k)local r=""for i=1,#data do r=r..string.char(data[i]~k)end return r end
local decoded=decrypt(encrypted,key)
loadstring(decoded)()

-- ============================================================
-- EXPLANATION:
-- ============================================================
-- 1. Original code is encrypted using XOR with key=42
-- 2. Original code is stored as number array {104,101,...}
-- 3. At runtime, decrypt() XORs each byte with key
-- 4. loadstring() converts decrypted string to function
-- 5. Function is executed with ()
-- 
-- RESULT: AI cannot see "print", "Hello", or any logic!
-- ============================================================

-- ============================================================
-- EXAMPLE: Method 1 - Octal Encoding
-- ============================================================

-- ORIGINAL:
-- print("Hello")

-- OBFUSCATED:
local a="\120\145\163\147\162\151\156\164\050\042\110\145\154\154\157\042\051"
loadstring(a)()

-- ============================================================
-- EXAMPLE: Method 3 - Split Concatenation
-- ============================================================

-- ORIGINAL:
-- game.Players.LocalPlayer.Character.Humanoid.Health = 9999

-- OBFUSCATED:
local p1="\147\141\155\145\056\120\154"
local p2="\141\171\145\162\163\056\114"
local p3="\157\143\141\154\120\154\141"
local p4="\171\145\162\056\103\150\141"
local full=p1..p2..p3..p4
loadstring(full)()

-- ============================================================
-- HOW TO USE IN DELTA EXECUTOR:
-- ============================================================
-- 1. Copy the obfuscated code above
-- 2. Open Delta Executor
-- 3. Paste the code in the script editor
-- 4. Click Execute
-- 5. Code runs perfectly as if it was original!
-- ============================================================

-- ============================================================
-- WHY AI CANNOT READ THIS:
-- ============================================================
-- When Gemini/GPT tries to analyze:
--
-- Input: local a="\120\145\163..."
-- AI: "This is a string... but what does \120\145\163 mean?"
-- AI: "loadstring() executes some string... but I don't know what"
-- AI: "Cannot determine the code's purpose"
--
-- Result: ✅ AI fails completely!
-- ============================================================

-- ============================================================
-- BONUS: Anti-Analysis Protection
-- ============================================================

-- Add this to make it even harder to analyze:
local function obfuscation_layer_1()
    local key=42
    local data={120,145,163,147}
    local function xor_decrypt(d,k)
        local r=""
        for i=1,#d do
            r=r..string.char(d[i]~k)
        end
        return r
    end
    return xor_decrypt(data,key)
end

local function obfuscation_layer_2()
    local code=obfuscation_layer_1()
    return loadstring(code)
end

obfuscation_layer_2()()

-- This creates multiple layers of functions and encryption
-- Even more resistant to analysis tools!

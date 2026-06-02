"""
Lua Obfuscator - Dynamic Code Generation with loadstring
Technique: Number 5 - Encode code as strings, execute via loadstring
No plaintext source code visible
"""

import base64
import random
import string


class LuaObfuscator:
    def __init__(self):
        self.encryption_key = random.randint(1, 255)
    
    # ============= ENCODING METHODS =============
    
    def encode_octal(self, text):
        """Convert text to octal escape sequences"""
        result = ""
        for char in text:
            result += f"\\{oct(ord(char))[2:].zfill(3)}"
        return result
    
    def encode_hex(self, text):
        """Convert text to hex escape sequences"""
        result = ""
        for char in text:
            result += f"\\x{ord(char):02x}"
        return result
    
    def encode_base64(self, text):
        """Convert text to base64"""
        return base64.b64encode(text.encode()).decode()
    
    def encode_xor(self, text, key):
        """XOR encryption of text"""
        result = []
        for char in text:
            result.append(ord(char) ^ key)
        return result
    
    def decode_xor(self, data, key):
        """XOR decryption"""
        result = ""
        for byte in data:
            result += chr(byte ^ key)
        return result
    
    # ============= OBFUSCATION METHODS =============
    
    def method_1_octal_encoding(self, lua_code):
        """Method 1: Simple Octal Encoding with loadstring"""
        encoded = self.encode_octal(lua_code)
        
        obfuscated = f'''local a="{encoded}"
loadstring(a)()'''
        return obfuscated
    
    def method_2_hex_encoding(self, lua_code):
        """Method 2: Hex Encoding with loadstring"""
        encoded = self.encode_hex(lua_code)
        
        obfuscated = f'''local b="{encoded}"
loadstring(b)()'''
        return obfuscated
    
    def method_3_split_concatenation(self, lua_code):
        """Method 3: Split code into parts and concatenate"""
        # Split into 4 random parts
        part_size = len(lua_code) // 4
        parts = [
            lua_code[0:part_size],
            lua_code[part_size:part_size*2],
            lua_code[part_size*2:part_size*3],
            lua_code[part_size*3:]
        ]
        
        # Encode each part
        encoded_parts = [self.encode_octal(part) for part in parts]
        
        obfuscated = f'''local p1="{encoded_parts[0]}"
local p2="{encoded_parts[1]}"
local p3="{encoded_parts[2]}"
local p4="{encoded_parts[3]}"
local full=p1..p2..p3..p4
loadstring(full)()'''
        return obfuscated
    
    def method_4_xor_encryption(self, lua_code):
        """Method 4: XOR Encryption with dynamic key"""
        key = self.encryption_key
        encrypted = self.encode_xor(lua_code, key)
        
        # Create array representation
        encrypted_str = "{" + ",".join(str(x) for x in encrypted) + "}"
        
        obfuscated = f'''local key={key}
local encrypted={encrypted_str}
local function decrypt(data,k)local r=""for i=1,#data do r=r..string.char(data[i]~k)end return r end
local decoded=decrypt(encrypted,key)
loadstring(decoded)()'''
        return obfuscated
    
    def method_5_base64_encoding(self, lua_code):
        """Method 5: Base64 Encoding (requires base64 library)"""
        encoded = self.encode_base64(lua_code)
        
        obfuscated = f'''local encoded="{encoded}"
local function b64decode(s)local b64chars="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"local t={{}}for i=1,#b64chars do t[b64chars:sub(i,i)]=i-1 end local r=""local p=0 for i=1,#s do local c=s:sub(i,i)if c~="="then p=p*64+t[c]if i%4==0 then r=r..string.char(bit.band(p,255))p=0 end end end return r end
local decoded=b64decode(encoded)
loadstring(decoded)()'''
        return obfuscated
    
    def method_6_complex_obfuscation(self, lua_code):
        """Method 6: Complex Multi-Layer Obfuscation"""
        # Layer 1: XOR encrypt
        key = self.encryption_key
        encrypted = self.encode_xor(lua_code, key)
        
        # Layer 2: Split into chunks
        chunk_size = max(1, len(encrypted) // 3)
        chunks = [encrypted[i:i+chunk_size] for i in range(0, len(encrypted), chunk_size)]
        
        # Layer 3: Create table representation
        chunk_arrays = ["{" + ",".join(str(x) for x in chunk) + "}" for chunk in chunks]
        
        chunk_3 = chunk_arrays[2] if len(chunk_arrays) > 2 else "{}"
        
        obfuscated = f'''local key={key}
local c1={chunk_arrays[0]}
local c2={chunk_arrays[1]}
local c3={chunk_3}
local chunks={{c1,c2,c3}}
local function decrypt_chunks()local result={{}}for _,chunk in ipairs(chunks)do for _,byte in ipairs(chunk)do table.insert(result,byte)end end local final=""for i=1,#result do final=final..string.char(result[i]~key)end return final end
local decoded=decrypt_chunks()
loadstring(decoded)()'''
        return obfuscated
    
    def method_7_function_wrapper(self, lua_code):
        """Method 7: Wrap code in function with encoded parameters"""
        encoded = self.encode_octal(lua_code)
        random_func = ''.join(random.choices(string.ascii_letters, k=8))
        
        obfuscated = f'''local function {random_func}()local x="{encoded}"return loadstring(x)end
{random_func}()()'''
        return obfuscated
    
    # ============= MAIN OBFUSCATE FUNCTION =============
    
    def obfuscate(self, lua_code, method=4):
        """
        Obfuscate Lua code using specified method
        Methods:
        1 = Octal Encoding
        2 = Hex Encoding
        3 = Split Concatenation
        4 = XOR Encryption (RECOMMENDED)
        5 = Base64 Encoding
        6 = Complex Multi-Layer
        7 = Function Wrapper
        """
        if method == 1:
            return self.method_1_octal_encoding(lua_code)
        elif method == 2:
            return self.method_2_hex_encoding(lua_code)
        elif method == 3:
            return self.method_3_split_concatenation(lua_code)
        elif method == 4:
            return self.method_4_xor_encryption(lua_code)
        elif method == 5:
            return self.method_5_base64_encoding(lua_code)
        elif method == 6:
            return self.method_6_complex_obfuscation(lua_code)
        elif method == 7:
            return self.method_7_function_wrapper(lua_code)
        else:
            return self.method_4_xor_encryption(lua_code)


# ============= USAGE EXAMPLE =============

if __name__ == "__main__":
    # Original Lua code
    original_code = '''print("Hello, World!")
local x = 10
local y = 20
print(x + y)'''
    
    obfuscator = LuaObfuscator()
    
    print("=" * 60)
    print("ORIGINAL CODE:")
    print("=" * 60)
    print(original_code)
    print()
    
    # Try all methods
    for method in range(1, 8):
        print("=" * 60)
        print(f"METHOD {method} (OBFUSCATED):")
        print("=" * 60)
        obfuscated = obfuscator.obfuscate(original_code, method=method)
        print(obfuscated)
        print()

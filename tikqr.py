#!/usr/bin/env python3
import base64
import json
import sys
from Crypto.Cipher import AES
from pyzbar.pyzbar import decode
from PIL import Image

# Key dari config
KEY = base64.b64decode("ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICA=")[:32]

def decrypt(b64):
    data = base64.b64decode(b64)
    cipher = AES.new(KEY, AES.MODE_GCM, nonce=data[:12])
    return cipher.decrypt_and_verify(data[12:-16], data[-16:]).decode()

def deep_decrypt(obj):
    if isinstance(obj, dict):
        return {k: deep_decrypt(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [deep_decrypt(i) for i in obj]
    if isinstance(obj, str):
        try:
            return decrypt(obj)
        except:
            return obj
    return obj

if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].lower().endswith('.jpg'):
        sys.exit(1)
    
    try:
        # Scan QR dari JPG
        qr_data = decode(Image.open(sys.argv[1]))[0].data.decode()
        
        # Decrypt utama
        decrypted = decrypt(qr_data)
        
        # Cari JSON
        json_start = decrypted.find('{')
        if json_start == -1:
            json_start = decrypted.find('[')
        
        # Parse dan deep decrypt
        data = json.loads(decrypted[json_start:])
        result = deep_decrypt(data)
        
        # Output JSON saja
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

from flask import Flask, request, Response
from flask_cors import CORS
import requests
import base64
import json
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

app = Flask(__name__)
CORS(app)

TOKEN = "8244921168:AAHRyemnt7kRBzSJT-QM6iExJHoPlDubgtM"
AES_KEY = b'mysecretkey12345678901234567890'  # 32 байта

def decrypt_aes(encrypted_b64):
    encrypted = base64.b64decode(encrypted_b64)
    iv = encrypted[:16]
    ciphertext = encrypted[16:]
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext)
    return unpad(decrypted, AES.block_size).decode('utf-8')

def encrypt_aes(data):
    cipher = AES.new(AES_KEY, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(data)
    iv = cipher.iv
    return base64.b64encode(iv + ct_bytes).decode('utf-8')

@app.route('/api', methods=['POST'])
def proxy():
    try:
        data = request.json
        if not data or 'data' not in data:
            return {"error": "No data"}, 400
        
        # Расшифровываем запрос
        decrypted = decrypt_aes(data['data'])
        payload = json.loads(decrypted)
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        if payload.get('type') == 'message':
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            tg_data = {
                'chat_id': payload['chat_id'],
                'text': payload['text'],
                'parse_mode': 'HTML'
            }
            resp = requests.post(url, json=tg_data, headers=headers, timeout=10)
            
        elif payload.get('type') == 'updates':
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            tg_data = {
                'timeout': 5,
                'offset': payload.get('offset', 0)
            }
            resp = requests.get(url, params=tg_data, headers=headers, timeout=10)
            
        else:
            return {"error": "Unknown type"}, 400
        
        # Шифруем ответ
        encrypted_response = encrypt_aes(resp.content)
        
        return {"data": encrypted_response}
        
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/health', methods=['GET'])
def health():
    return {"status": "ok"}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

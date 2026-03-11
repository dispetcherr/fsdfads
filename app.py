from flask import Flask, request, Response
from flask_cors import CORS
import requests
import base64
import json
import time
import random
import os
import traceback

app = Flask(__name__)
CORS(app)

# ТВОЙ ТОКЕН
TOKEN = "8244921168:AAF4I9ptSwQN1pUCp1f5oHFoUSUD3IyzU0Y"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0"
]

@app.route('/api', methods=['POST'])
def proxy():
    try:
        data = request.json
        if not data or 'data' not in data:
            return {"error": "No data"}, 400
        
        encrypted = data['data']
        
        # Расшифровка с обработкой ошибок
        try:
            decoded = base64.b64decode(encrypted).decode('utf-8', errors='ignore')
            decrypted = ''.join(chr(ord(c) ^ 0x3A) for c in decoded)
            payload = json.loads(decrypted)
        except Exception as e:
            return {"error": f"Decryption failed: {str(e)}"}, 400
        
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        
        if payload.get('type') == 'message':
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            tg_data = {
                'chat_id': payload['chat_id'],
                'text': payload['text'],
                'parse_mode': 'HTML'
            }
            resp = requests.post(url, json=tg_data, headers=headers, timeout=30)
            
        elif payload.get('type') == 'updates':
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
            tg_data = {
                'timeout': payload.get('timeout', 30),
                'offset': payload.get('offset', 0)
            }
            resp = requests.get(url, params=tg_data, headers=headers, timeout=35)
            
        else:
            return {"error": "Unknown type"}, 400
        
        time.sleep(random.uniform(0.3, 1.0))
        
        return Response(resp.content, resp.status_code, mimetype='application/json')
        
    except Exception as e:
        # Логируем ошибку
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        return {"error": str(e)}, 500

@app.route('/health', methods=['GET'])
def health():
    return {"status": "ok", "time": time.time()}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

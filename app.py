from flask import Flask, request, Response
from flask_cors import CORS
import requests
import base64
import json
import os
import traceback

app = Flask(__name__)
CORS(app)

# ТВОЙ НОВЫЙ ТОКЕН
TOKEN = "8244921168:AAHRyemnt7kRBzSJT-QM6iExJHoPlDubgtM"

@app.route('/api', methods=['POST'])
def proxy():
    try:
        data = request.json
        if not data or 'data' not in data:
            return {"error": "No data"}, 400
        
        encrypted = data['data']
        
        # Расшифровка
        decoded = base64.b64decode(encrypted).decode('utf-8', errors='ignore')
        decrypted = ''.join(chr(ord(c) ^ 0x3A) for c in decoded)
        payload = json.loads(decrypted)
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
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
        
        return Response(resp.content, resp.status_code, mimetype='application/json')
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {"error": str(e)}, 500

@app.route('/health', methods=['GET'])
def health():
    return {"status": "ok"}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

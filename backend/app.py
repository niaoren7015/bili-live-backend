import os
import json
import hmac
import hashlib
import uuid
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 从环境变量获取API凭证
ACCESS_KEY_ID = os.environ.get('ACCESS_KEY_ID')
ACCESS_KEY_SECRET = os.environ.get('ACCESS_KEY_SECRET')
APP_ID = os.environ.get('APP_ID')

def generate_signature(body):
    """
    生成B站API签名
    """
    timestamp = str(int(datetime.now().timestamp()))
    nonce = str(uuid.uuid4())
    content_md5 = hashlib.md5(body.strip().encode()).hexdigest()
    
    sign_str = f"x-bili-accesskeyid:{ACCESS_KEY_ID}\n" \
               f"x-bili-content-md5:{content_md5}\n" \
               f"x-bili-signature-method:HMAC-SHA256\n" \
               f"x-bili-signature-nonce:{nonce}\n" \
               f"x-bili-signature-version:1.0\n" \
               f"x-bili-timestamp:{timestamp}"
    
    signature = hmac.new(
        ACCESS_KEY_SECRET.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest().lower()

    return {
        'signature': signature,
        'timestamp': timestamp,
        'nonce': nonce,
        'content_md5': content_md5
    }

@app.route('/start', methods=['POST'])
def start_live():
    try:
        code = request.json.get('code')
        request_body = json.dumps({
            "code": code,
            "app_id": APP_ID
        }, separators=(',', ':'))

        # 生成签名
        sign_info = generate_signature(request_body)
        
        # 构建请求头
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-bili-accesskeyid": ACCESS_KEY_ID,
            "x-bili-content-md5": sign_info['content_md5'], 
            "x-bili-signature-method": "HMAC-SHA256",
            "x-bili-signature-nonce": sign_info['nonce'],
            "x-bili-signature-version": "1.0",
            "x-bili-timestamp": sign_info['timestamp'],
            "Authorization": sign_info['signature']
        }

        # 调用B站API
        response = requests.post(
            "https://live-open.biliapi.com/v2/app/start",
            headers=headers,
            data=request_body
        )
        
        if response.status_code == 200:
            return jsonify(response.json()['data'])
        else:
            return jsonify({"error": "API调用失败", "details": response.text}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)
CORS(app)

# 核心修改：让 Python 负责显示你的 index.html
@app.route('/')
def home():
    # 尝试从根目录读取 index.html
    return send_from_directory('..', 'index.html')

@app.route('/api/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url:
        return jsonify({"status": "error", "message": "链接为空"})

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # 尝试解析接口
    try:
        res = requests.get(f"https://www.tikwm.com/api/?url={url}", headers=headers, timeout=10, verify=False).json()
        if res.get('code') == 0:
            v_url = res['data']['play']
            if not v_url.startswith('http'):
                v_url = "https://www.tikwm.com" + v_url
            title = res['data'].get('title', 'tiktok_video')
            return jsonify({"status": "success", "url": v_url, "title": title[:40]})
    except Exception:
        pass

    return jsonify({"status": "error", "message": "云端解析暂不可用，请稍后再试"})

if __name__ == '__main__':
    app.run()

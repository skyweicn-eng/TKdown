from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)
CORS(app)

@app.route('/api/download', methods=['POST'])
def download():
    raw_url = request.json.get('url', '')
    if not raw_url:
        return jsonify({"status": "error", "message": "链接为空"})

    # 核心优化：清洗链接，去掉问号后面的追踪参数，大幅提升解析成功率！
    url = raw_url.split('?')[0]

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

    # 1. 尝试 TikWM 接口
    try:
        res = requests.get(f"https://www.tikwm.com/api/?url={url}", headers=headers, timeout=8, verify=False).json()
        if res.get('code') == 0:
            v_url = res['data']['play']
            if not v_url.startswith('http'):
                v_url = "https://www.tikwm.com" + v_url
            title = res['data'].get('title', '无文案描述')
            author = res['data'].get('author', {}).get('nickname', '未知作者')
            return jsonify({"status": "success", "url": v_url, "title": title, "author": author})
    except Exception:
        pass

    # 2. 尝试 TiklyDown 接口作备用
    try:
        res = requests.get(f"https://api.tiklydown.eu.org/api/download?url={url}", headers=headers, timeout=8, verify=False).json()
        if 'video' in res:
            v_url = res['video'].get('noWatermark') or res['video'].get('url')
            title = res.get('title', '无文案描述')
            author = res.get('author', {}).get('name', '未知作者')
            return jsonify({"status": "success", "url": v_url, "title": title, "author": author})
    except Exception:
        return jsonify({"status": "error", "message": "云端接口均超时，请稍后重试"})

    return jsonify({"status": "error", "message": "该视频可能已被删除或隐藏"})

if __name__ == '__main__':
    app.run()

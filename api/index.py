from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)
CORS(app)

@app.route('/api/download', methods=['POST'])
def download():
    url = request.json.get('url')
    if not url:
        return jsonify({"status": "error", "message": "链接为空"})

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # 优先尝试 TikWM 接口
    try:
        res = requests.get(f"https://www.tikwm.com/api/?url={url}", headers=headers, timeout=10, verify=False).json()
        if res.get('code') == 0:
            v_url = res['data']['play']
            if not v_url.startswith('http'):
                v_url = "https://www.tikwm.com" + v_url
            title = res['data'].get('title', 'tiktok_video')
            return jsonify({"status": "success", "url": v_url, "title": title[:40]})
    except Exception:
        pass # 失败则继续尝试下一个

    # 备用尝试 TiklyDown 接口
    try:
        res = requests.get(f"https://api.tiklydown.eu.org/api/download?url={url}", headers=headers, timeout=10, verify=False).json()
        if 'video' in res:
            v_url = res['video'].get('noWatermark') or res['video'].get('url')
            title = res.get('title', 'tiktok_video')
            return jsonify({"status": "success", "url": v_url, "title": title[:40]})
    except Exception:
        return jsonify({"status": "error", "message": "云端解析彻底失败"})

    return jsonify({"status": "error", "message": "无法提取该视频"})

# 适配 Vercel 的 Serverless 启动方式
if __name__ == '__main__':
    app.run()

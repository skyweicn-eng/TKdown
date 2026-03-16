from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)
CORS(app)

# ==========================================
# 终极杀手锏：将前端网页直接嵌入后端，彻底消灭 404！
# ==========================================
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TIKTOK MASTER - 终极稳定版</title>
    <style>
        body { background: #0f0f0f; color: #e0e0e0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; flex-direction: column; align-items: center; padding: 40px 20px; margin: 0; }
        .box { background: #1a1a1a; padding: 25px; border-radius: 12px; width: 100%; max-width: 700px; border: 1px solid #333; box-shadow: 0 10px 40px rgba(0,0,0,0.6); box-sizing: border-box; }
        h1 { text-align: center; background: linear-gradient(45deg, #00f2ea, #ff0050); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0 0 20px 0; font-size: 26px; font-weight: 800; }
        textarea { width: 100%; height: 140px; background: #0a0a0a; border: 1px solid #444; color: #00f2ea; padding: 15px; border-radius: 8px; box-sizing: border-box; font-family: monospace; font-size: 12px; line-height: 1.5; outline: none; margin-bottom: 15px; resize: vertical; }
        textarea:focus { border-color: #00f2ea; }
        .btn-group { display: flex; gap: 12px; }
        button { flex: 1; border: none; padding: 14px; color: white; font-weight: bold; border-radius: 8px; cursor: pointer; font-size: 15px; transition: 0.2s; box-sizing: border-box; }
        .btn-parse { background: #ff0050; }
        .btn-parse:hover { background: #d40042; }
        .btn-dl-all { background: #00f2ea; color: #000; display: none; }
        .btn-dl-all:hover { background: #00c4bd; }
        #log { margin-top: 25px; width: 100%; max-width: 700px; box-sizing: border-box; }
        .item { background: #222; padding: 15px; border-radius: 8px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: flex-start; border-left: 4px solid #00f2ea; box-sizing: border-box; }
        .info { display: flex; flex-direction: column; width: 80%; padding-right: 15px; }
        .author { font-weight: bold; color: #00f2ea; font-size: 13px; margin-bottom: 6px; }
        .desc { font-size: 12px; color: #bbb; line-height: 1.6; word-wrap: break-word; white-space: normal; }
        .dl-btn { background: #333; border: 1px solid #555; color: #fff; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: bold; cursor: pointer; transition: 0.2s; white-space: nowrap; align-self: center; }
        .dl-btn:hover { background: #444; color: #00f2ea; border-color: #00f2ea; }
    </style>
</head>
<body>
    <div class="box">
        <h1>TIKTOK MASTER Cloud</h1>
        <textarea id="links" placeholder="在这里粘贴 TikTok 链接，支持批量输入，每行一个..."></textarea>
        <div class="btn-group">
            <button class="btn-parse" onclick="startCloudParse()">🔥 批量极速解析</button>
            <button id="dlAllBtn" class="btn-dl-all" onclick="downloadAll()">⬇️ 一键下载全部</button>
        </div>
    </div>
    <div id="log"></div>

    <script>
        let parsedVideos = [];

        async function startCloudParse() {
            const area = document.getElementById('links');
            const log = document.getElementById('log');
            const dlAllBtn = document.getElementById('dlAllBtn');
            const lines = area.value.split('\n').map(s => s.trim()).filter(s => s.startsWith('http'));

            if (lines.length === 0) return alert('请先粘贴视频链接！');
            
            parsedVideos = []; 
            log.innerHTML = '<div style="color:#888; text-align:center; font-size: 13px;">🚀 服务器正在拼命解析中，请稍候...</div>';
            dlAllBtn.style.display = 'none';

            for (let url of lines) {
                try {
                    const response = await fetch('/api/download', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ url: url })
                    });
                    const data = await response.json();
                    const div = document.createElement('div');
                    div.className = 'item';
                    
                    if (data.status === 'success') {
                        parsedVideos.push(data.url);
                        div.innerHTML = `
                            <div class="info">
                                <span class="author">👤 ${data.author}</span>
                                <span class="desc">${data.title}</span>
                            </div>
                            <button onclick="triggerDownload('${data.url}')" class="dl-btn">下载视频</button>
                        `;
                    } else {
                        div.style.borderLeftColor = '#ff4d4d';
                        div.innerHTML = `<span style="color:#ff4d4d; font-size: 13px;">❌ 解析失败: ${data.message}</span>`;
                    }
                    log.appendChild(div);
                } catch (e) {
                    const err = document.createElement('div');
                    err.className = 'item';
                    err.style.borderLeftColor = '#ffcc00';
                    err.innerHTML = `<span style="color:#ffcc00; font-size: 13px;">⚠️ 网络异常或该链接格式无法识别</span>`;
                    log.appendChild(err);
                }
            }

            if (parsedVideos.length > 0) {
                dlAllBtn.style.display = 'block';
                log.firstChild.innerHTML = `<span style="color:#10b981; font-weight:bold;">✅ 解析完成！共成功提取 ${parsedVideos.length} 个视频。</span>`;
            }
        }

        function triggerDownload(url) {
            const a = document.createElement('a');
            a.href = url;
            a.target = '_blank'; 
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }

        function downloadAll() {
            if (parsedVideos.length === 0) return;
            
            alert(`即将触发 ${parsedVideos.length} 个视频下载。\n\n⚠️ 如果浏览器顶部提示“已拦截弹出式窗口”，请务必点击并选择“始终允许”。`);
            
            parsedVideos.forEach((url, index) => {
                setTimeout(() => {
                    triggerDownload(url);
                }, index * 800); 
            });
        }
    </script>
</body>
</html>"""
# ==========================================


@app.route('/')
def home():
    # 当访问首页时，直接返回上面写好的 HTML 代码
    return HTML_PAGE

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

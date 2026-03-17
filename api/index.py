from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)
CORS(app)

# ==========================================
# 终极全栈代码：强制静默下载 + 防卡死排队
# ==========================================
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TIKTOK MASTER - 稳定批量版</title>
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
        .dl-btn:disabled { background: #222; color: #666; cursor: not-allowed; border-color: #333; }
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
        let btnCounter = 0;

        async function startCloudParse() {
            const area = document.getElementById('links');
            const log = document.getElementById('log');
            const dlAllBtn = document.getElementById('dlAllBtn');
            const lines = area.value.split('\n').map(s => s.trim()).filter(s => s.startsWith('http'));

            if (lines.length === 0) return alert('请先粘贴视频链接！');
            
            parsedVideos = []; 
            log.innerHTML = '<div style="color:#888; text-align:center; font-size: 13px; margin-bottom: 10px;">🚀 服务器正在拼命解析中，请稍候...</div>';
            dlAllBtn.style.display = 'none';

            for (let i = 0; i < lines.length; i++) {
                let url = lines[i];
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
                        btnCounter++;
                        const btnId = 'dl-btn-' + btnCounter;
                        parsedVideos.push({ url: data.url, title: data.title, id: btnId });
                        const currentIndex = parsedVideos.length - 1;

                        div.innerHTML = `
                            <div class="info">
                                <span class="author">👤 ${data.author}</span>
                                <span class="desc">${data.title}</span>
                            </div>
                            <button id="${btnId}" onclick="triggerDownloadByIndex(${currentIndex})" class="dl-btn">强制下载</button>
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

                if (i < lines.length - 1) {
                    const waitDiv = document.createElement('div');
                    waitDiv.innerHTML = '<span style="color:#666; font-size: 12px;">⏳ 防封控安全缓冲 2 秒...</span>';
                    waitDiv.style.textAlign = 'center';
                    waitDiv.style.marginBottom = '12px';
                    log.appendChild(waitDiv);
                    await new Promise(resolve => setTimeout(resolve, 2000)); 
                    waitDiv.remove(); 
                }
            }

            if (parsedVideos.length > 0) {
                dlAllBtn.style.display = 'block';
                log.firstChild.innerHTML = `<span style="color:#10b981; font-weight:bold;">✅ 解析完成！共成功提取 ${parsedVideos.length} 个视频。</span>`;
            } else {
                log.firstChild.innerHTML = `<span style="color:#ff4d4d; font-weight:bold;">❌ 解析结束，没有成功提取到视频。</span>`;
            }
        }

        // 核心：强制数据流下载逻辑
        async function triggerDownloadByIndex(index) {
            const video = parsedVideos[index];
            const btn = document.getElementById(video.id);
            
            if (btn) {
                btn.innerText = "⏳ 抽取中...";
                btn.style.background = "#ffcc00";
                btn.style.color = "#000";
                btn.disabled = true;
            }

            try {
                // 尝试跨域拉取数据流
                let res = await fetch(video.url).catch(() => null);
                
                // 如果遭遇严格跨域拦截，启用公益代理强行拉取
                if (!res || !res.ok) {
                    res = await fetch('https://corsproxy.io/?' + encodeURIComponent(video.url));
                }
                
                // 转为 Blob 二进制对象
                const blob = await res.blob();
                const blobUrl = window.URL.createObjectURL(blob);
                
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = blobUrl;
                // 清洗文件名中的非法符号
                let safeTitle = video.title.replace(/[\\/:*?"<>|]/g, "").substring(0, 40);
                a.download = (safeTitle || "tiktok_video") + ".mp4";
                
                document.body.appendChild(a);
                a.click();
                
                document.body.removeChild(a);
                window.URL.revokeObjectURL(blobUrl);

                if (btn) {
                    btn.innerText = "✅ 已保存";
                    btn.style.background = "#10b981";
                    btn.style.color = "#fff";
                }
            } catch (error) {
                console.error("数据流下载失败，回退旧方案", error);
                // 极低概率的失败备用案：弹出新窗口
                const a = document.createElement('a');
                a.href = video.url;
                a.target = '_blank';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                
                if (btn) {
                    btn.innerText = "⚠️ 需手动保存";
                    btn.style.background = "#444";
                    btn.style.color = "#fff";
                }
            }
            if(btn) btn.disabled = false;
        }

        async function downloadAll() {
            if (parsedVideos.length === 0) return;
            
            const dlAllBtn = document.getElementById('dlAllBtn');
            dlAllBtn.innerText = "⏳ 正在依次写入硬盘，请勿关闭网页...";
            dlAllBtn.disabled = true;

            for (let i = 0; i < parsedVideos.length; i++) {
                await triggerDownloadByIndex(i);
                // 强制排队：下完一个等 1.5 秒再下另一个，防止浏览器崩盘
                await new Promise(resolve => setTimeout(resolve, 1500)); 
            }
            
            dlAllBtn.innerText = "✅ 全部下载完毕";
            setTimeout(() => {
                dlAllBtn.innerText = "⬇️ 一键下载全部";
                dlAllBtn.disabled = false;
            }, 3000);
        }
    </script>
</body>
</html>"""
# ==========================================


@app.route('/')
def home():
    return HTML_PAGE

@app.route('/api/download', methods=['POST'])
def download():
    raw_url = request.json.get('url', '')
    if not raw_url:
        return jsonify({"status": "error", "message": "链接为空"})

    url = raw_url.split('?')[0]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

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

    try:
        res = requests.get(f"https://api.tiklydown.eu.org/api/download?url={url}", headers=headers, timeout=8, verify=False).json()
        if 'video' in res:
            v_url = res['video'].get('noWatermark') or res['video'].get('url')
            title = res.get('title', '无文案描述')
            author = res.get('author', {}).get('name', '未知作者')
            return jsonify({"status": "success", "url": v_url, "title": title, "author": author})
    except Exception:
        return jsonify({"status": "error", "message": "云端接口均超时，请稍后重试"})

    return jsonify({"status": "error", "message": "该视频可能已被删除或接口失效"})

if __name__ == '__main__':
    app.run()

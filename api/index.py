from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
app = Flask(__name__)
CORS(app)

# ==========================================
# 终极全栈代码：带专属密码锁 + UI 深度美化
# 保持核心逻辑绝对不变
# ==========================================
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TIKTOK MASTER - Daiway 专属版</title>
    <style>
        :root {
            --primary: #00f2ea;
            --secondary: #ff0050;
            --bg-color: #0d0d0f;
            --card-bg: rgba(25, 25, 30, 0.6);
        }
        body { 
            background: var(--bg-color); 
            background-image: radial-gradient(circle at top right, rgba(255,0,80,0.08), transparent 40%),
                              radial-gradient(circle at bottom left, rgba(0,242,234,0.08), transparent 40%);
            color: #e0e0e0; 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            padding: 50px 20px; 
            margin: 0; 
            min-height: 100vh;
        }
        
        /* --- 密码锁屏专属样式 --- */
        #lock-screen {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: var(--bg-color);
            background-image: radial-gradient(circle at center, rgba(0,242,234,0.1), transparent 60%);
            display: flex; justify-content: center; align-items: center;
            z-index: 9999;
            transition: opacity 0.5s ease;
        }
        .lock-box {
            background: var(--card-bg);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            padding: 40px; border-radius: 20px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 20px 50px rgba(0,0,0,0.8);
            width: 90%; max-width: 380px;
        }
        .lock-box h2 {
            margin: 0 0 10px 0;
            font-size: 24px;
            background: linear-gradient(45deg, var(--primary), #fff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .lock-hint { color: #888; font-size: 13px; margin-bottom: 25px; letter-spacing: 1px;}
        .lock-input {
            width: 100%; padding: 15px; background: rgba(0,0,0,0.5);
            border: 1px solid #444; color: var(--primary);
            border-radius: 10px; font-size: 20px; text-align: center;
            box-sizing: border-box; outline: none; transition: 0.3s;
            letter-spacing: 5px; margin-bottom: 20px; font-weight: bold;
        }
        .lock-input:focus { border-color: var(--primary); box-shadow: 0 0 15px rgba(0,242,234,0.2); }
        .lock-btn {
            width: 100%; padding: 14px; background: linear-gradient(45deg, var(--primary), #00c4bd);
            color: #000; font-weight: bold; border: none; border-radius: 10px;
            font-size: 16px; cursor: pointer; transition: 0.3s;
        }
        .lock-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,242,234,0.3); }
        .lock-error { color: #ff4d4d; font-size: 13px; margin-top: 15px; height: 18px; }

        /* --- 工作台样式 --- */
        .box { 
            background: var(--card-bg); 
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 35px; 
            border-radius: 20px; 
            width: 100%; 
            max-width: 700px; 
            border: 1px solid rgba(255,255,255,0.05); 
            box-shadow: 0 20px 50px rgba(0,0,0,0.5); 
            box-sizing: border-box; 
        }
        h1 { 
            text-align: center; 
            background: linear-gradient(135deg, var(--primary), var(--secondary)); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            margin: 0 0 25px 0; 
            font-size: 32px; 
            font-weight: 900; 
            letter-spacing: 1px;
        }
        textarea { 
            width: 100%; 
            height: 150px; 
            background: rgba(0,0,0,0.4); 
            border: 1px solid rgba(255,255,255,0.1); 
            color: var(--primary); 
            padding: 18px; 
            border-radius: 12px; 
            box-sizing: border-box; 
            font-family: 'Courier New', Courier, monospace; 
            font-size: 13px; 
            line-height: 1.6; 
            outline: none; 
            margin-bottom: 20px; 
            resize: vertical; 
            transition: all 0.3s ease;
        }
        textarea:focus { border-color: var(--primary); box-shadow: 0 0 15px rgba(0,242,234,0.1); }
        .btn-group { display: flex; gap: 15px; }
        button { 
            flex: 1; border: none; padding: 16px; color: white; font-weight: bold; 
            border-radius: 12px; cursor: pointer; font-size: 16px; transition: all 0.3s ease; 
            box-sizing: border-box; text-transform: uppercase; letter-spacing: 0.5px;
        }
        .btn-parse { background: linear-gradient(45deg, var(--secondary), #d40042); box-shadow: 0 4px 15px rgba(255,0,80,0.25); }
        .btn-parse:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(255,0,80,0.4); }
        .btn-dl-all { background: linear-gradient(45deg, var(--primary), #00c4bd); color: #000; display: none; box-shadow: 0 4px 15px rgba(0,242,234,0.25); }
        .btn-dl-all:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,242,234,0.4); }
        #log { margin-top: 30px; width: 100%; max-width: 700px; box-sizing: border-box; }
        .item { 
            background: rgba(30, 30, 35, 0.7); backdrop-filter: blur(8px);
            padding: 18px; border-radius: 12px; margin-bottom: 15px; display: flex; 
            justify-content: space-between; align-items: center; border-left: 4px solid var(--primary); 
            box-sizing: border-box; border-top: 1px solid rgba(255,255,255,0.03);
            border-right: 1px solid rgba(255,255,255,0.03); border-bottom: 1px solid rgba(255,255,255,0.03);
            transition: transform 0.2s ease;
        }
        .item:hover { transform: translateX(2px); }
        .info { display: flex; flex-direction: column; width: 78%; padding-right: 15px; }
        .author { font-weight: bold; color: var(--primary); font-size: 14px; margin-bottom: 8px; }
        .desc { font-size: 13px; color: #ccc; line-height: 1.6; word-wrap: break-word; white-space: normal; }
        .dl-btn { 
            background: #2a2a2a; border: 1px solid #444; color: #fff; padding: 10px 18px; 
            border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: bold; 
            cursor: pointer; transition: all 0.2s ease; white-space: nowrap; text-transform: none; letter-spacing: normal;
        }
        .dl-btn:hover { background: #333; color: var(--primary); border-color: var(--primary); }
        .dl-btn:disabled { background: #222; color: #666; cursor: not-allowed; border-color: #333; }
        
        .footer {
            margin-top: auto; padding-top: 50px; padding-bottom: 20px;
            text-align: center; color: #666; font-size: 13px; letter-spacing: 1px;
        }
        .footer span { color: var(--primary); font-weight: bold; }
    </style>
</head>
<body>

    <!-- 专属密码锁屏 -->
    <div id="lock-screen">
        <div class="lock-box">
            <h2>🔒 专属工具验证</h2>
            <div class="lock-hint">口令提示：一个发财佬发发发</div>
            <input type="password" id="pwd" class="lock-input" placeholder="请输入口令" onkeypress="if(event.keyCode===13) checkPwd()">
            <button class="lock-btn" onclick="checkPwd()">解锁工作台</button>
            <div id="lock-error" class="lock-error"></div>
        </div>
    </div>

    <!-- 核心工作台 -->
    <div class="box">
        <h1>TIKTOK MASTER</h1>
        <textarea id="links" placeholder="在这里粘贴 TikTok 链接，支持批量输入，每行一个..."></textarea>
        <div class="btn-group">
            <button class="btn-parse" onclick="startCloudParse()">🔥 批量极速解析</button>
            <button id="dlAllBtn" class="btn-dl-all" onclick="downloadAll()">⬇️ 一键下载全部</button>
        </div>
    </div>
    <div id="log"></div>
    
    <!-- 底部专属标识与版本号 -->
    <div class="footer">
        Powered by Vercel Serverless | <span>Daiway 专属定制</span> | Version 2.2.0 Pro
    </div>

    <script>
        // --- 密码锁验证逻辑 ---
        document.addEventListener('DOMContentLoaded', () => {
            // 如果本地缓存中存有凭证，直接隐藏密码锁
            if (localStorage.getItem('daiway_vip_auth') === '888') {
                document.getElementById('lock-screen').style.display = 'none';
            }
        });

        function checkPwd() {
            const pwd = document.getElementById('pwd').value;
            const errorDiv = document.getElementById('lock-error');
            
            if (pwd === '888') {
                // 验证成功，写入本地缓存
                localStorage.setItem('daiway_vip_auth', '888');
                const lockScreen = document.getElementById('lock-screen');
                lockScreen.style.opacity = '0'; // 触发淡出动画
                setTimeout(() => { lockScreen.style.display = 'none'; }, 500);
            } else {
                errorDiv.innerText = '❌ 专属口令错误，无法访问';
                document.getElementById('pwd').value = ''; // 清空输入框
                setTimeout(() => { errorDiv.innerText = ''; }, 2000); // 2秒后清除错误提示
            }
        }

        // --- 核心解析与下载逻辑 (保持不变) ---
        let parsedVideos = [];
        let btnCounter = 0;

        async function startCloudParse() {
            const area = document.getElementById('links');
            const log = document.getElementById('log');
            const dlAllBtn = document.getElementById('dlAllBtn');
            const lines = area.value.split('\n').map(s => s.trim()).filter(s => s.startsWith('http'));

            if (lines.length === 0) return alert('请先粘贴视频链接！');
            
            parsedVideos = []; 
            log.innerHTML = '<div style="color:#888; text-align:center; font-size: 14px; margin-bottom: 15px;">🚀 引擎全开，正在深度解析中...</div>';
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
                            <button id="${btnId}" onclick="triggerDownloadByIndex(${currentIndex})" class="dl-btn">静默下载</button>
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
                    err.innerHTML = `<span style="color:#ffcc00; font-size: 13px;">⚠️ 网络波动或链接格式异常</span>`;
                    log.appendChild(err);
                }

                if (i < lines.length - 1) {
                    const waitDiv = document.createElement('div');
                    waitDiv.innerHTML = '<span style="color:#666; font-size: 13px;">⏳ 防封控安全缓冲 2 秒...</span>';
                    waitDiv.style.textAlign = 'center';
                    waitDiv.style.marginBottom = '15px';
                    log.appendChild(waitDiv);
                    await new Promise(resolve => setTimeout(resolve, 2000)); 
                    waitDiv.remove(); 
                }
            }

            if (parsedVideos.length > 0) {
                dlAllBtn.style.display = 'block';
                log.firstChild.innerHTML = `<span style="color:#10b981; font-weight:bold; font-size: 14px;">✅ 解析完成！共成功提取 ${parsedVideos.length} 个高清视频源。</span>`;
            } else {
                log.firstChild.innerHTML = `<span style="color:#ff4d4d; font-weight:bold; font-size: 14px;">❌ 解析结束，暂未提取到有效视频。</span>`;
            }
        }

        async function triggerDownloadByIndex(index) {
            const video = parsedVideos[index];
            const btn = document.getElementById(video.id);
            
            if (btn) {
                btn.innerText = "⏳ 抽取中...";
                btn.style.background = "linear-gradient(45deg, #f59e0b, #d97706)";
                btn.style.color = "#fff";
                btn.style.borderColor = "#d97706";
                btn.disabled = true;
            }

            try {
                let res = await fetch(video.url).catch(() => null);
                if (!res || !res.ok) {
                    res = await fetch('https://corsproxy.io/?' + encodeURIComponent(video.url));
                }
                const blob = await res.blob();
                const blobUrl = window.URL.createObjectURL(blob);
                
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = blobUrl;
                let safeTitle = video.title.replace(/[\\/:*?"<>|]/g, "").substring(0, 40);
                a.download = (safeTitle || "tiktok_master_video") + ".mp4";
                
                document.body.appendChild(a);
                a.click();
                
                document.body.removeChild(a);
                window.URL.revokeObjectURL(blobUrl);

                if (btn) {
                    btn.innerText = "✅ 已存本地";
                    btn.style.background = "linear-gradient(45deg, #10b981, #059669)";
                    btn.style.borderColor = "#059669";
                }
            } catch (error) {
                console.error("流抽取失败，执行备用方案", error);
                const a = document.createElement('a');
                a.href = video.url;
                a.target = '_blank';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                
                if (btn) {
                    btn.innerText = "⚠️ 需手动保存";
                    btn.style.background = "#444";
                }
            }
            if(btn) btn.disabled = false;
        }

        async function downloadAll() {
            if (parsedVideos.length === 0) return;
            
            const dlAllBtn = document.getElementById('dlAllBtn');
            dlAllBtn.innerText = "⏳ 正在高速写入本地，请勿关闭页面...";
            dlAllBtn.disabled = true;

            for (let i = 0; i < parsedVideos.length; i++) {
                await triggerDownloadByIndex(i);
                await new Promise(resolve => setTimeout(resolve, 1500)); 
            }
            
            dlAllBtn.innerText = "✅ 批量下载任务完成";
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

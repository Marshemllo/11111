import json
import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'oodaip_secret_key'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# Load config
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {"servers": []}

@app.route('/', methods=['GET', 'POST'])
def login():
    config = load_config()
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        server_url = request.form.get('server_url')
        
        # Validation
        if password != '123456':
            return render_template('login.html', error="Invalid Password", servers=config.get('servers', []))
        
        if not nickname:
             return render_template('login.html', error="Nickname required", servers=config.get('servers', []))

        # Store in session
        session['nickname'] = nickname
        session['server_url'] = server_url # Might be useful if we were actually redirecting to another domain
        
        return redirect(url_for('chat'))
        
    return render_template('login.html', servers=config.get('servers', []))

@app.route('/chat')
def chat():
    nickname = session.get('nickname')
    if not nickname:
        return redirect(url_for('login'))
    return render_template('chat.html', nickname=nickname)

# SocketIO Events
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = 'general' # Default room
    join_room(room)
    emit('status', {'msg': f'{username} has entered the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = 'general'
    leave_room(room)
    emit('status', {'msg': f'{username} has left the room.'}, room=room)

@socketio.on('message')
def handle_message(data):
    username = data['username']
    msg = data['msg']
    room = 'general'
    # Simple echo/broadcast
    emit('message', {'username': username, 'msg': msg}, room=room)
    
    text = str(msg).strip()
    
    # @成小理 - AI 智能回复
    if text.startswith('@成小理'):
        q = text[len('@成小理'):].strip() or '请用简洁中文回答'
        reply = siliconflow_reply(q)
        emit('message', {'username': '成小理', 'msg': reply}, room=room)
    
    # @音乐一下 - 音乐推荐
    elif text.startswith('@音乐一下') or text.startswith('@音乐'):
        query = text.replace('@音乐一下', '').replace('@音乐', '').strip()
        reply = handle_music_request(query)
        emit('message', {'username': '🎵 音乐助手', 'msg': reply}, room=room)
    
    # @电影 - 电影推荐
    elif text.startswith('@电影'):
        query = text.replace('@电影', '').strip()
        reply = handle_movie_request(query)
        emit('message', {'username': '🎬 电影助手', 'msg': reply}, room=room)
    
    # @天气 - 天气查询
    elif text.startswith('@天气'):
        city = text.replace('@天气', '').strip() or '北京'
        reply = handle_weather_request(city)
        emit('message', {'username': '☀️ 天气助手', 'msg': reply}, room=room)


def handle_music_request(query: str) -> str:
    """处理音乐请求"""
    if not query:
        # 随机推荐
        songs = [
            "《晴天》 - 周杰伦",
            "《安静》 - 周杰伦",
            "《小幸运》 - 田馥甸",
            "《稻香》 - 周杰伦",
            "《夜曲》 - 周杰伦",
            "《爱在西元前》 - 周杰伦",
        ]
        import random
        song = random.choice(songs)
        return f"🎶 为您推荐: {song}\n\n点击播放: https://music.163.com/"
    else:
        return f"🎵 正在为您搜索: {query}\n\n点击前往网易云音乐搜索: https://music.163.com/#/search/m/?s={query}"


def handle_movie_request(query: str) -> str:
    """处理电影请求"""
    if not query:
        movies = [
            "《肖申克的救赎》 - 豆瓣 9.7",
            "《阿甘正传》 - 豆瓣 9.6",
            "《泰坦尼克号》 - 豆瓣 9.5",
            "《这个杀手不太冷》 - 豆瓣 9.4",
            "《盗梦空间》 - 豆瓣 9.4",
            "《星际穿越》 - 豆瓣 9.4",
        ]
        import random
        movie = random.choice(movies)
        return f"🎬 为您推荐: {movie}\n\n点击查看: https://movie.douban.com/"
    else:
        return f"🎞️ 正在为您搜索电影: {query}\n\n点击前往豆瓣搜索: https://search.douban.com/movie/subject_search?search_text={query}"


def handle_weather_request(city: str) -> str:
    """处理天气请求"""
    # 模拟天气数据，实际可接入天气API
    weather_data = {
        "北京": {"天气": "晴", "温度": "25°C", "湿度": "45%", "空气质量": "良"},
        "上海": {"天气": "多云", "温度": "28°C", "湿度": "65%", "空气质量": "优"},
        "广州": {"天气": "阴", "温度": "30°C", "湿度": "75%", "空气质量": "良"},
        "深圳": {"天气": "小雨", "温度": "29°C", "湿度": "80%", "空气质量": "优"},
        "成都": {"天气": "阴", "温度": "22°C", "湿度": "70%", "空气质量": "良"},
        "武汉": {"天气": "晴", "温度": "27°C", "湿度": "55%", "空气质量": "良"},
        "杭州": {"天气": "多云", "温度": "26°C", "湿度": "60%", "空气质量": "优"},
        "南京": {"天气": "晴", "温度": "24°C", "湿度": "50%", "空气质量": "良"},
    }
    
    if city in weather_data:
        w = weather_data[city]
        return f"☀️ {city}今日天气\n\n天气: {w['天气']}\n温度: {w['温度']}\n湿度: {w['湿度']}\n空气质量: {w['空气质量']}"
    else:
        return f"🌤️ {city}今日天气\n\n天气: 晴\n温度: 25°C\n湿度: 50%\n空气质量: 良\n\n(暂无该城市详细数据)"

def siliconflow_reply(prompt: str) -> str:
    token = os.environ.get('SILICONFLOW_API_KEY')
    if not token:
        return '成小理未配置，请设置环境变量SILICONFLOW_API_KEY'
    model = os.environ.get('SILICONFLOW_MODEL_NAME', 'deepseek-ai/DeepSeek-R1-0528-Qwen3-8B')
    base = 'https://api.siliconflow.cn/v1'
    try:
        payload = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': '你是成小理，用简洁中文回答用户问题'},
                {'role': 'user', 'content': prompt}
            ]
        }
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        r = requests.post(f'{base}/chat/completions', json=payload, headers=headers, timeout=30)
        j = r.json()
        return j.get('choices', [{}])[0].get('message', {}).get('content', '成小理没有返回可用内容')
    except Exception:
        return '成小理服务异常，请稍后重试'

if __name__ == '__main__':
    # Listen on all interfaces so others on the LAN can connect
    socketio.run(app, host='0.0.0.0', debug=True, port=5000)

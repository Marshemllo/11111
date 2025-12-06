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
    # Logic for @mentions can be processed here or on client. 
    # Requirement: "receive and response". We just broadcast.
    emit('message', {'username': username, 'msg': msg}, room=room)
    text = str(msg).strip()
    if text.startswith('@成小理'):
        q = text[len('@成小理'):].strip() or '请用简洁中文回答'
        reply = siliconflow_reply(q)
        emit('message', {'username': '成小理', 'msg': reply}, room=room)

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

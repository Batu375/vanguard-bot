import discord
from discord.ext import commands
from flask import Flask, render_template, request, redirect, session
import threading
import json
import requests
import os

# --- 1. WEB SUNUCUSU (FLASK) AYARLARI ---
app = Flask(__name__)
app.secret_key = os.urandom(24)

# SENİN BİLGİLERİN SİSTEME EKLENDİ
CLIENT_ID = '1494358859471651008'
CLIENT_SECRET = 'DsDcieFSTeM-yWjmJrr5xji9Fm_Wt64d'
BOT_TOKEN = 'MTQ5NDM1ODg1OTQ3MTY1MTAwOA.GmBFI8.EuaWfDF7AKjI45VxuoYUaVVQysaUYMTkvoX2kM' # Sadece bunu sen gireceksin!

# Şimdilik yerel test linkimiz (Buluta yüklerken bunu değiştireceğiz)
REDIRECT_URI = 'http://127.0.0.1:5000/callback' 

@app.route('/')
def home():
    try:
        with open("stats.json", "r") as f:
            stats = json.load(f)
    except:
        stats = {"server_count": 0, "member_count": 0}
    return render_template('index.html', stats=stats, user=session.get('user'))

@app.route('/login')
def login():
    oauth_url = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=identify"
    return redirect(oauth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code: return redirect('/')
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    token_response = r.json()
    if 'access_token' not in token_response: 
        return f"Giriş Hatası: {token_response}"
    
    token = token_response['access_token']
    user_response = requests.get('https://discord.com/api/users/@me', headers={'Authorization': f'Bearer {token}'})
    user_data = user_response.json()
    avatar_url = f"https://cdn.discordapp.com/avatars/{user_data.get('id')}/{user_data.get('avatar')}.png" if user_data.get('avatar') else "https://cdn.discordapp.com/embed/avatars/0.png"
    session['user'] = {'id': user_data.get('id'), 'username': user_data.get('username'), 'avatar': avatar_url}
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Bulut sistemleri için Web sunucusunu başlatan fonksiyon
def run_web():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# --- 2. DISCORD BOT AYARLARI ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"--- Vanguard Bot Aktif! ({bot.user.name}) ---")
    
# --- 3. SİSTEMİ ATEŞLEME ---
if __name__ == '__main__':
    # Web sunucusunu arka planda başlat
    threading.Thread(target=run_web, daemon=True).start()
    # Botu çalıştır
    bot.run(BOT_TOKEN)
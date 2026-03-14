import ssl
ssl._create_default_https_context = ssl._create_unverified_context

import threading
import webbrowser
import time
import sys
import os
import tkinter as tk

def resource_path(relative):
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)

from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp
import tempfile

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_from_directory(resource_path('static'), 'index.html')

@app.route('/info')
def info():
    url = request.args.get('url', '')
    ydl_opts = {'quiet': True, 'no_warnings': True, 'nocheckcertificate': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(url, download=False)
        return jsonify({
            'title': data.get('title', 'Unknown'),
            'channel': data.get('uploader', '-'),
            'duration': data.get('duration', 0),
            'view_count': data.get('view_count', 0),
            'thumbnail': data.get('thumbnail', ''),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/download')
def download():
    url     = request.args.get('url', '')
    quality = request.args.get('quality', '2160')
    fmt     = request.args.get('format', 'mp4')
    subs    = request.args.get('subtitles') == 'true'
    thumb   = request.args.get('thumbnail') == 'true'
    meta    = request.args.get('metadata')  == 'true'

    tmp = tempfile.mkdtemp()
    out = os.path.join(tmp, '%(title)s.%(ext)s')

    ffmpeg_loc = None
    possible = [
        r'C:\ffmpeg\bin',
        r'C:\Program Files\ffmpeg\bin',
        os.path.join(os.environ.get('USERPROFILE', ''), 'ffmpeg', 'bin'),
    ]
    for p in possible:
        if os.path.exists(os.path.join(p, 'ffmpeg.exe')):
            ffmpeg_loc = p
            break

    if quality == 'audio':
        fmt_str   = 'bestaudio/best'
        postprocs = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]
    else:
        fmt_str   = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]'
        postprocs = [{'key': 'FFmpegVideoConvertor', 'preferedformat': fmt}]

    opts = {
        'format': fmt_str, 'outtmpl': out, 'postprocessors': postprocs,
        'writesubtitles': subs, 'embedthumbnail': thumb, 'addmetadata': meta,
        'quiet': True, 'no_warnings': True, 'nocheckcertificate': True,
    }
    if ffmpeg_loc:
        opts['ffmpeg_location'] = ffmpeg_loc

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info_data = ydl.extract_info(url, download=True)
            filename  = ydl.prepare_filename(info_data)
            base      = os.path.splitext(filename)[0]
            for f in os.listdir(tmp):
                if f.startswith(os.path.basename(base)):
                    return send_file(os.path.join(tmp, f), as_attachment=True, download_name=f)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'File not found'}), 500

def run_server():
    app.run(host='127.0.0.1', port=8080, debug=False, use_reloader=False)

def launch_gui():
    root = tk.Tk()
    root.title('VidGrab')
    root.geometry('300x160')
    root.resizable(False, False)
    root.configure(bg='#0a0a0c')

    tk.Label(root, text='VidGrab', font=('Helvetica', 16, 'bold'),
             bg='#0a0a0c', fg='#ff2d2d').pack(pady=(20, 4))
    tk.Label(root, text='Server is running...', font=('Helvetica', 10),
             bg='#0a0a0c', fg='#5a5a6e').pack()

    status_var = tk.StringVar(value='Ready')
    tk.Label(root, textvariable=status_var, font=('Helvetica', 10),
             bg='#0a0a0c', fg='#2dff8f').pack(pady=4)

    def open_app():
        webbrowser.open('http://127.0.0.1:8080')
        status_var.set('Opened in browser')

    def quit_app():
        root.destroy()
        os._exit(0)

    btn_frame = tk.Frame(root, bg='#0a0a0c')
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text='Open App', command=open_app,
              bg='#ff2d2d', fg='white', relief='flat',
              padx=14, pady=6, font=('Helvetica', 10, 'bold')).pack(side='left', padx=6)

    tk.Button(btn_frame, text='Quit', command=quit_app,
              bg='#1e1e26', fg='#f0eee8', relief='flat',
              padx=14, pady=6, font=('Helvetica', 10)).pack(side='left', padx=6)

    root.mainloop()

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1.2)
    webbrowser.open('http://127.0.0.1:8080')
    launch_gui()

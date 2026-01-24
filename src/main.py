import hashlib
from io import BytesIO
import platform
import queue
import shutil
import subprocess
import sys
import threading
import time
current_exe = sys.executable
try:
    from PIL import Image, ImageTk
    import requests
    import tkinter as tk
    import yt_dlp
    import dependencies
    import video
except Exception as e:
    print("error importing: "+e)
    time.sleep(1)
    subprocess.Popen([current_exe] + sys.argv[1:])
    time.sleep(1)
    sys.exit(0)

url = "https://api.github.com/repos/anuser88/yt-player2/releases/latest"
r = requests.get(url)
r.raise_for_status()
release = r.json()
def file_sha256(path):
    hash_sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return "sha256:" + hash_sha256.hexdigest()
assets = release["assets"]
osname = platform.system()
if osname == "Windows":
    asset = assets[2]
if osname == "Linux":
    asset = assets[0]
if osname == "Darwin":
    asset = assets[1]
download_url = asset["browser_download_url"]
filename = asset["name"]
latest_version = release["tag_name"]
backup_exe = current_exe + ".bak"
CURRENT_VERSION="version-unknown"
if file_sha256(current_exe) == asset["digest"] or not getattr(sys, "frozen", False):
    CURRENT_VERSION=latest_version
    print("Already up-to-date")
    if os.path.exists(backup_exe):
        if input("Would you like to remove old version backup[y/n]").lower() == "y":
            os.remove(backup_exe)
else:
    try:
        tmp_path = os.path.join(os.path.dirname(sys.executable), f"new_{filename}")
        print("trying to update")
        for i in range(0, 3):
            print("attempt #" + str(i + 1))
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(tmp_path, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
            # stream download
            if file_sha256(tmp_path) == asset["digest"]:
                os.rename(current_exe, backup_exe)
                os.rename(tmp_path, current_exe)
                time.sleep(1)
                subprocess.Popen([current_exe] + sys.argv[1:])
                time.sleep(1)
                sys.exit(0)
                # restart
        os.remove(tmp_path)
        raise Exception("download failed")
    except Exception as e:
        print("update failed: " + e)

class exited:
    def __init__(self):
        self.e=False
    def exit(self):
        self.e=True
    def stat(self):
        return self.e

def search(query,q,resn=5):
    recommendations = []
    ydl_opts = {
        'extract_flat': True,
        'noplaylist': True,
        'quiet': True,
        'ignoreerrors': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }
    }
    t=time.time()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{resn}:{query}", download=False)
        for entry in info['entries']:
            q.put({
                "title": entry.get('title'),
                "link": entry.get('webpage_url'),
                "id": entry.get('id')
            })
            print(entry.get('webpage_url'))
    return time.time()-t

# --- GUI ---
def show(q,frame,root):
    try:
        while True:
            rec=q.get_nowait()
            if rec=="taskkill":
                return sys.exit()
            if rec['id']:
                response = requests.get(f"https://img.youtube.com/vi/{rec['id']}/hqdefault.jpg")
                img_data = Image.open(BytesIO(response.content))
                img_data = img_data.resize((320, 180))
                img = ImageTk.PhotoImage(img_data)
                lbl = tk.Label(frame, image=img)
                lbl.image = img
                lbl.pack(pady=5)
                lbl.bind("<Button-1>", lambda e, url=f"https://youtube.com/watch?v={rec['id']}": video.createplayer(url,1080).start())
            tl=tk.Label(frame, text=rec['title'], wraplength=400, font=("Arial", 12, "bold"))
            tl.pack(padx=20, pady=10, anchor="center")
            tl.bind("<Button-1>", lambda e, url=f"https://youtube.com/watch?v={rec['id']}": video.createplayer(url,1080).start())
    except queue.Empty:
        pass
    root.after(50, show, q, frame, root)

def clear_rec(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def prompt(q,frame,ex):
    inp=""
    print("Type 'help' for more info")
    while not ex.stat():
        inp=input(">>>")
        if inp=="help":
            print("Type 'search' to search")
            print("Type 'watch' to watch from an URL")
            print("Type 'clear' to clear search result")
            print("Type 'exit' to quit")
        if inp=="search":
            print(f"Searched in {search(input('Search anything: '),q,resn=input("Number of result: "))} sec")
            print("Rendering...")
        if inp=="clear":
            clear_rec(frame)
        if inp=="watch":
            video.createplayer(input("URL: "),1080).start()
        if inp=="exit":
            q.put("taskkill")
            return

def start():
    print("\nyt-player2 " + CURRENT_VERSION)    
    root = tk.Tk()
    root.title("YouTube Search")
    canvas = tk.Canvas(root, width=450, height=600)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    frame = tk.Frame(canvas)
    frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0,0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    q=queue.Queue()
    ex=exited()
    s=threading.Thread(target=prompt, args=(q,frame,ex))
    s.start()
    clear_rec(frame)
    show(q,frame,root)
    root.mainloop()
    ex.exit()
    print("Press enter to exit")
    sys.exit()
start()

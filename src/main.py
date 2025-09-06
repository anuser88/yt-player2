import dependencies
from io import BytesIO
from PIL import Image, ImageTk
import queue
import requests
import sys
import threading
import time
import tkinter as tk
import video
import yt_dlp

class exited:
    def __init__(self):
        self.e=False
    def exit(self):
        self.e=True
    def stat(self):
        return self.e

def search(query,q):
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
        info = ydl.extract_info(f"ytsearch50:{query}", download=False)
        for entry in info['entries']:
            q.put({
                "title": entry.get('title'),
                "link": entry.get('webpage_url'),
                "id": entry.get('id')
            })
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
            print(f"Searched in {search(input('Search anything: '),q)} sec")
            print("Rendering...")
        if inp=="clear":
            clear_rec(frame)
        if inp=="watch":
            video.createplayer(input("URL: "),1080).start()
        if inp=="exit":
            q.put("taskkill")
            return

def start():
    print("\nyt-player2 v1.0.2")    
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

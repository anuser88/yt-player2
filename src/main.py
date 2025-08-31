import dependencies
from io import BytesIO
from PIL import Image, ImageTk
import queue
import requests
import threading
import time
import tkinter as tk
import video
import yt_dlp

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
                return
            tl=tk.Label(frame, text=rec['title'], wraplength=400, justify="left", font=("Arial", 12, "bold"))
            tl.pack(pady=5, anchor="w")
            tl.bind("<Button-1>", lambda e, url=f"https://youtube.com/watch?v={rec['id']}": video.createplayer(url,720).start())
            if rec['id']:
                response = requests.get(f"https://img.youtube.com/vi/{rec['id']}/hqdefault.jpg")
                img_data = Image.open(BytesIO(response.content))
                img_data = img_data.resize((320, 180))
                img = ImageTk.PhotoImage(img_data)
                lbl = tk.Label(frame, image=img)
                lbl.image = img
                lbl.pack(pady=5)
                lbl.bind("<Button-1>", lambda e, url=f"https://youtube.com/watch?v={rec['id']}": video.createplayer(url,720).start())
    except queue.Empty:
        pass
    root.after(50, show, q, frame, root)

def clear_rec(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def prompt(q,frame):
    inp=""
    print("Type 'help' for more info")
    while inp!="exit":
        inp=input(">>>")
        if inp=="help":
            print("Type 'search' to search")
            print("Type 'clear' to clear search result")
            print("Type 'exit' to quit")
        if inp=="search":
            print(f"Searched in {search(input('Search anything: '),q)} sec")
            print("Rendering...")
        if inp=="clear":
            clear_rec(frame)
        if inp=="exit":
            q.put("taskkill")

def start():
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
    s=threading.Thread(target=prompt, args=(q,frame,))
    s.start()
    clear_rec(frame)
    show(q,frame,root)
    root.mainloop()
    s.join()
start()

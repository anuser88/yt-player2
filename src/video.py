import subprocess
import threading
import time
import yt_dlp
def play(VIDEO_URL,res=720):
    print("Preparing...")
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(VIDEO_URL, download=False)
        video_title = info.get('title', 'YouTube Video')
    cmd = ["yt-dlp","-f", "best", "-S", "+height:"+str(res), "-o", "-",VIDEO_URL]
    ffplay = subprocess.Popen(["ffplay", "-autoexit", "-window_title", video_title, "-i", "pipe:0"],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
    with subprocess.Popen(cmd, stdout=ffplay.stdin) as ytdlp_proc:
        ytdlp_proc.communicate()
    time.sleep(1.5)
    input("Enter to close...")
    ffplay.terminate()
def createplayer(url,res):
    return threading.Thread(target=play, args=(url,res,))
if __name__=="__main__":
    play("https://youtube.com/watch?v=dQw4w9WgXcQ")

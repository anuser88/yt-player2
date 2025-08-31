import subprocess
import threading
import yt_dlp
def play(VIDEO_URL):
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(VIDEO_URL, download=False)
        video_title = info.get('title', 'YouTube Video')
    cmd = ["yt-dlp","-f", "best","-o", "-",VIDEO_URL]
    ffplay = subprocess.Popen(["ffplay", "-autoexit", "-window_title", video_title, "-i", "pipe:0"],stdin=subprocess.PIPE)
    with subprocess.Popen(cmd, stdout=ffplay.stdin) as ytdlp_proc:
        ytdlp_proc.communicate()
    ffplay.wait()
def createplayer(url):
    return threading.Thread(target=play, args=(url,))
if __name__=="__main__":
    play("https://youtube.com/watch?v=dQw4w9WgXcQ")

import os
import sys
import subprocess
import platform
import zipfile
import tarfile
import urllib.request
import shutil

def is_ffmpeg_installed():
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def is_ytdlp_installed():
    try:
        subprocess.run(['yt-dlp', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def download_ffmpeg_windows(dest_folder):
    url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    zip_path = os.path.join(dest_folder, "ffmpeg.zip")
    os.makedirs(dest_folder, exist_ok=True)
    print("Downloading FFmpeg for Windows...")
    urllib.request.urlretrieve(url, zip_path)
    print("Extracting FFmpeg...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_folder)
    os.remove(zip_path)
    bin_path = os.path.join(dest_folder, os.listdir(dest_folder)[0], "bin")
    return bin_path

def download_ffmpeg_unix(dest_folder):
    url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    tar_path = os.path.join(dest_folder, "ffmpeg.tar.xz")
    os.makedirs(dest_folder, exist_ok=True)
    print("Downloading FFmpeg for Unix...")
    urllib.request.urlretrieve(url, tar_path)
    print("Extracting FFmpeg...")
    with tarfile.open(tar_path) as tar_ref:
        tar_ref.extractall(dest_folder)
    os.remove(tar_path)
    # The folder usually ends with "ffmpeg-*-amd64-static"
    folder = next(f for f in os.listdir(dest_folder) if f.startswith("ffmpeg") and os.path.isdir(os.path.join(dest_folder, f)))
    bin_path = os.path.join(dest_folder, folder)
    return bin_path

def add_to_path(bin_path):
    if platform.system() == "Windows":
        current_path = os.environ["PATH"]
        if bin_path not in current_path:
            subprocess.run(f'setx PATH "{bin_path};%PATH%"', shell=True)
    else:
        shell_profile = os.path.expanduser("~/.bashrc")
        with open(shell_profile, "a") as f:
            f.write(f'\nexport PATH="{bin_path}:$PATH"\n')
        print(f"Run `source {shell_profile}` or restart your terminal to use FFmpeg.")

system = platform.system()
if not is_ffmpeg_installed():
    print("FFmpeg not found. Installing...")
    dest_folder = os.path.join(os.path.expanduser("~"), "ffmpeg")
    if system == "Windows":
        bin_path = download_ffmpeg_windows(dest_folder)
    else:
        bin_path = download_ffmpeg_unix(dest_folder)
    add_to_path(bin_path)
    print("FFmpeg installation completed.")
else:
    print("FFmpeg is already installed.")

if not is_ytdlp_installed():
    print("yt-dlp not found. Installing...")
    dest_folder = os.path.join(os.path.expanduser("~"), "yt-dlp")
    if system == "Windows":
        save_path = os.path.join(dest_folder, "yt-dlp.exe")
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    else:
        save_path = os.path.join(dest_folder, "yt-dlp")
        url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
    urllib.request.urlretrieve(url, save_path)
    add_to_path(dest_folder)
    print("yt-dlp installation completed.")
else:
    print("yt-dlp is already installed.")

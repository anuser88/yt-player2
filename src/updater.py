import requests, hashlib, os, platform, sys, shutil, subprocess
UPDATE = False

with open("version.txt","r") as f:
    CURRENT_VERSION = f.read()
    f.close()

def file_sha256(path):
    hash_sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return "sha256:" + hash_sha256.hexdigest()

url = "https://api.github.com/repos/anuser88/yt-player2/releases/latest"
r = requests.get(url)
r.raise_for_status()
release = r.json()
latest_version = release["tag_name"]

if latest_version == CURRENT_VERSION or getattr(sys, "frozen", False):
    print("Already up-to-date")
else:
    UPDATE = True

if UPDATE:
    try:
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

        tmp_path = os.path.join(os.path.dirname(sys.executable), f"new_{filename}")
        for i in range(0, 3):
            print("Attempt #" + str(i + 1))
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(tmp_path, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
            # stream download
            if file_sha256(tmp_path) == asset["digest"]:

                current_exe = sys.executable
                backup_exe = current_exe + ".bak"
                os.rename(current_exe, backup_exe)

                os.rename(tmp_path, current_exe)

                subprocess.Popen([current_exe] + sys.argv[1:])
                sys.exit(0)
                # restart
        os.remove(tmp_path)
        raise Exception("download failed")
    except Exception as e
        print("update failed: " + e)
    
    

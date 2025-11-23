import requests, os, platform, sys, shutil, subprocess
UPDATE = False

with open("version.txt","r") as f:
    CURRENT_VERSION = f.read()
    f.close()

url = "https://api.github.com/repos/anuser88/yt-player2/releases/latest"
r = requests.get(url)
r.raise_for_status()
release = r.json()
latest_version = release["tag_name"]

if latest_version == CURRENT_VERSION or getattr(sys, "frozen", False):
    print("Already up-to-date")
    UPDATE = True

if UPDATE:
    asset = release["assets"][0]
    download_url = asset["browser_download_url"]
    filename = asset["name"]

    tmp_path = os.path.join(os.path.dirname(sys.executable), f"new_{filename}")
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(r.raw, f)
    # stream download

    current_exe = sys.executable
    backup_exe = current_exe + ".bak"
    try:
        os.rename(current_exe, backup_exe)
    except Exception as e:
        print("Cannot rename old exe:", e)

    os.rename(tmp_path, current_exe)

    subprocess.Popen([current_exe] + sys.argv[1:])
    sys.exit(0)
    # restart

import sys
import requests
import json
from time import strftime, localtime
from tqdm import tqdm
from rclone_python import rclone

args = sys.argv[1:]

def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

MAIN_GOPRO_URL = "http://10.5.5.9:8080"

if (args[0] and args[0] == "enableusb"):
    print('Enabling wired control...')
    requests.get(MAIN_GOPRO_URL + '/gopro/camera/control/wired_usb?p=1')
    print('Enabled!')

if (args[0] and args[0] == "parseserial"):
    print(f'USB Serial Socket: 172.2{args[1][-3]}.1{args[1][-2]}{args[1][-1]}.51:8080')

if (args[0] and args[0] == "disableusb"):
    print('Disabling wired control...')
    requests.get(MAIN_GOPRO_URL + '/gopro/camera/control/wired_usb?p=0')
    print('Disabled!')

if (args[0] and args[0] == "view"):
    finalFiles = {
        'files': []
    }

    filesResp = requests.get(MAIN_GOPRO_URL + '/gopro/media/list')
    filesJson = filesResp.json()

    print("DIR NAME: " + filesJson['media'][0]['d'] + "\n")

    for file in filesJson['media'][0]['fs']:
        finalFiles['files'].append({
            'name': file['n'],
            'size': sizeof_fmt(int(file['s'])),
            'lastModified': strftime('%Y-%m-%d %H:%M:%S', localtime(int(file['mod'])))
        })

    print(json.dumps(finalFiles, indent=1))

if (args[0] and args[0] == "download"):
    direct = args[1]
    fileName = args[2]

    print("Enabling Turbo Transfer...")
    requests.get(MAIN_GOPRO_URL + '/gopro/media/turbo_transfer?p=1')
    print("Turbo Enabled")

    print("Downloading: " + direct + "/" + fileName)

    file = requests.get(MAIN_GOPRO_URL + '/videos/DCIM/' + direct + '/' + fileName, stream=True)
    total_size = int(file.headers.get("content-length", 0))
    block_size = 1024

    with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
        with open(fileName, "wb") as download:
            for data in file.iter_content(block_size):
                progress_bar.update(len(data))
                download.write(data)
    if total_size != 0 and progress_bar.n != total_size:
        raise RuntimeError("Could not download file")
    
    print("Downloaded! Disabling Turbo Transfer...")
    requests.get(MAIN_GOPRO_URL + '/gopro/media/turbo_transfer?p=0')
    print("Turbo Disabled")

    if (args[3] == 'up'):
        rclone.copy(fileName, f'shsdrive:{fileName}')

if (args[0] and args[0] == "upload"):
    rclone.copy(args[1], f'shsdrive:{args[1]}')


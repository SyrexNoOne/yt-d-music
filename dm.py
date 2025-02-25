import os
import subprocess
import ssl
import sys
import shutil
import yt_dlp

# Tu dong cai dat thu vien neu chua co
def install_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Cai dat {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_package("rich")

from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn

console = Console()

def check_ssl():
    console.print("[bold cyan]Kiem tra ho tro SSL...[/bold cyan]")
    if not hasattr(ssl, 'SSLContext'):
        raise RuntimeError("Moi truong Python cua ban khong ho tro SSL.")
    console.print("[green]SSL san sang.[/green]")

def check_ffmpeg():
    console.print("[bold cyan]Kiem tra ffmpeg...[/bold cyan]")
    if shutil.which("ffmpeg"):
        console.print("[green]ffmpeg san sang.[/green]")
        return True
    console.print("[red]Loi: 'ffmpeg' chua duoc cai dat. Dang tien hanh cai dat...[/red]")
    
    # Tu dong cai ffmpeg
    if sys.platform.startswith("linux"):
        subprocess.run(["sudo", "apt", "install", "-y", "ffmpeg"])
    elif sys.platform == "darwin":  # macOS
        subprocess.run(["brew", "install", "ffmpeg"])
    elif sys.platform == "win32":  # Windows
        console.print("[yellow]Vui long tai ffmpeg thu cong tu https://ffmpeg.org/download.html[/yellow]")

    return bool(shutil.which("ffmpeg"))

def download_audio(url, title):
    console.print(f"[bold yellow]Dang tai: {title}[/bold yellow]")
    download_path = os.path.join(os.path.expanduser("~"), "Downloads", f"{title}.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': download_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("Dang tai...", total=100)
            ydl.download([url])
            progress.update(task, completed=100)

    console.print(f"[green]Tai xuong hoan tat: {download_path}[/green]")

def search_and_download(song_name):
    console.print(f"[bold cyan]Dang tim kiem: {song_name}[/bold cyan]")
    check_ssl()
    search_query = f"ytsearch5:{song_name}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        console.print("Dang lay thong tin bai hat...")
        info = ydl.extract_info(search_query, download=False)

        if 'entries' in info and info['entries']:
            console.print("[bold green]Danh sach bai hat tim thay:[/bold green]")
            for i, entry in enumerate(info['entries'], 1):
                console.print(f"[cyan]{i}. {entry['title']}[/cyan]")

            choice = input("Chon bai hat (1-5) hoac 'exit' de huy: ")
            if choice.lower() == "exit":
                return

            try:
                index = int(choice) - 1
                if 0 <= index < len(info['entries']):
                    video_url = info['entries'][index]['url']
                    title = info['entries'][index]['title']
                    console.print(f"[bold green]Dang tai: {title}[/bold green]")
                    if check_ffmpeg():
                        download_audio(video_url, title)
                else:
                    console.print("[red]Lua chon khong hop le.[/red]")
            except ValueError:
                console.print("[red]Vui long nhap mot so hop le.[/red]")
        else:
            console.print("[red]Khong tim thay ket qua![/red]")

if __name__ == "__main__":
    while True:
        song_name = input("Nhap ten bai hat (hoac 'exit' de thoat): ")
        if song_name.lower() == "exit":
            console.print("[bold red]Dang thoat...[/bold red]")
            break
        search_and_download(song_name)
import yt_dlp
import tkinter as tk
from tkinter import filedialog

def download_youtube(url, download_type="video"):
    # Ask user where to save file
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    if download_type == "audio":
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("Audio Files", "*.mp3"), ("All Files", "*.*")],
            title="Save audio as..."
        )
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': file_path
        }
    else:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("Video Files", "*.mp4"), ("All Files", "*.*")],
            title="Save video as..."
        )
        ydl_opts = {
            'format': 'best',
            'outtmpl': file_path
        }

    if file_path:  # Only download if user selected a file
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"{download_type.capitalize()} saved as: {file_path}")
    else:
        print("Download cancelled.")

# Example usage
video_url = input("Enter YouTube video URL: ").strip()
download_type = input("Download type (video/audio): ").strip().lower()

download_youtube(video_url, download_type)

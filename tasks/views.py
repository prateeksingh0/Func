# views.py
from django.shortcuts import render
from django.conf import settings
from django.http import FileResponse, HttpResponse, StreamingHttpResponse
from .forms import YouTubeForm
import yt_dlp
import os
import subprocess

# DOWNLOAD_FOLDER = "media"

# os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def home(request):
    return render(request, "home.html")

def yd(request):
    # if request.method == "POST":
    #     form = YouTubeForm(request.POST)
    #     if form.is_valid():
    #         url = form.cleaned_data['url']
    #         download_type = form.cleaned_data['download_type']

    #         # Temporary file path
    #         file_path = os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s")

    #         ydl_opts = {
    #             'format': 'bestaudio/best' if download_type == "audio" else 'best',
    #             'outtmpl': file_path,
    #             'cookiefile': os.path.join(DOWNLOAD_FOLDER,'cookie.txt'),
    #         }

    #         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #             info = ydl.extract_info(url, download=True)
    #             filename = ydl.prepare_filename(info)

    #         settings.YT_DOWNLOAD_FILE_PATH = filename
    #         # Serve file as download
    #         if os.path.exists(filename):
    #             file = open(filename, 'rb')
    #             response = FileResponse(file)
    #             response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
                
    #             return response
    #         else:
    #             return HttpResponse("Error: File not found.")

    # else:
    #     form = YouTubeForm()

    # return render(request, "yd.html", {'form': form})
    if request.method == "POST":
        form = YouTubeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            download_type = form.cleaned_data['download_type']  # "audio" or "video"

            try:
                # Set file extension and yt-dlp format
                ext = "mp3" if download_type == "audio" else "mp4"
                ydl_format = "bestaudio/best" if download_type == "audio" else "best"

                # Generator to stream yt-dlp output
                def stream_generator():
                    cmd = [
                        "yt-dlp",
                        "-f", ydl_format,
                        url,
                        "-o", "-",  # write to stdout
                    ]
                    # For audio conversion to mp3
                    if download_type == "audio":
                        cmd += ["--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"]

                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                    for chunk in iter(lambda: process.stdout.read(4096), b""):
                        yield chunk
                    process.stdout.close()
                    process.wait()

                # Prepare filename for browser
                filename = f"youtube_download.{ext}"

                response = StreamingHttpResponse(
                    stream_generator(),
                    content_type="application/octet-stream"
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response

            except Exception as e:
                return HttpResponse(f"Error: {str(e)}", status=500)

    else:
        form = YouTubeForm()

    return render(request, "yd.html", {'form': form})

def share(request):
    return render(request, "fileshare.html")

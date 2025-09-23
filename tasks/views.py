# views.py
from django.shortcuts import render
from django.conf import settings
from django.http import FileResponse, HttpResponse, StreamingHttpResponse
from .forms import YouTubeForm
import yt_dlp
import os
import subprocess
import requests

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
                ydl_opts = {
                    'format': 'bestaudio/best' if download_type=='audio' else 'best',
                    'quiet': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    media_url = info.get('url')
                    ext = info.get('ext', 'mp4')
                    title = info.get('title', 'youtube')
                    filename = f"{title}.{ext}"

                if not media_url:
                    return HttpResponse("Cannot fetch media URL", status=400)

                # Stream media via requests in large chunks
                def stream_generator():
                    with requests.get(media_url, stream=True) as r:
                        for chunk in r.iter_content(chunk_size=1024*64):
                            if chunk:
                                yield chunk

                response = StreamingHttpResponse(stream_generator(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response

            except Exception as e:
                return HttpResponse(f"Error: {str(e)}", status=500)

    else:
        form = YouTubeForm()

    return render(request, "yd.html", {'form': form})

def share(request):
    return render(request, "fileshare.html")

# views.py
from django.shortcuts import render
from django.conf import settings
from django.http import FileResponse, HttpResponse, StreamingHttpResponse, HttpResponseRedirect
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
                    'noplaylist': True  # optional: avoid playlists
                }

                # Extract media info and direct URL
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    media_url = info.get('url')

                if not media_url:
                    return HttpResponse("Cannot fetch media URL. Video may be restricted or require sign-in.", status=400)

                # Redirect the user to the direct media URL
                return HttpResponseRedirect(media_url)

            except yt_dlp.utils.DownloadError:
                return HttpResponse("This video cannot be downloaded without sign-in or is restricted.", status=403)
            except Exception as e:
                return HttpResponse(f"Error: {str(e)}", status=500)

    else:
        form = YouTubeForm()

    return render(request, "yd.html", {'form': form})

def share(request):
    return render(request, "fileshare.html")

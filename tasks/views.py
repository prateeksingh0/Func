# views.py
from django.shortcuts import render
from django.conf import settings
from django.http import FileResponse, HttpResponse
from .forms import YouTubeForm
import yt_dlp
import os

DOWNLOAD_FOLDER = "media"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def yd(request):
    if request.method == "POST":
        form = YouTubeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            download_type = form.cleaned_data['download_type']

            # Temporary file path
            file_path = os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s")

            ydl_opts = {
                'format': 'bestaudio/best' if download_type == "audio" else 'best',
                'outtmpl': file_path
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            settings.YT_DOWNLOAD_FILE_PATH = filename
            # Serve file as download
            if os.path.exists(filename):
                file = open(filename, 'rb')
                response = FileResponse(file)
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
                
                return response
            else:
                return HttpResponse("Error: File not found.")

    else:
        form = YouTubeForm()

    return render(request, "yd.html", {'form': form})

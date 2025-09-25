# views.py
from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from .forms import YouTubeForm
import yt_dlp
import os, tempfile
from django.conf import settings


def home(request):
    return render(request, "home.html")

def yd(request):
    if request.method == "POST":
        form = YouTubeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            download_type = form.cleaned_data['download_type']
            
            cookies_content = os.getenv("YTDLP_COOKIES")
            if not cookies_content:
                return HttpResponse("No cookies found in environment variables.", status=500)
            with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as tmp_cookie_file:
                tmp_cookie_file.write(cookies_content)
                tmp_cookie_file.close()
                cookies_file_path = tmp_cookie_file.name

            temp_dir = tempfile.mkdtemp()

            ydl_opts = {
                'format': 'bestaudio/best' if download_type == "audio" else 'bestvideo+bestaudio/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'cookiefile': cookies_file_path,
                'quiet':True
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)
                    except yt_dlp.utils.ExtractorError:
                        return HttpResponse(
                            "Requested format is not available for this video.", status=400
                        )
                    except yt_dlp.utils.DownloadError:
                        return HttpResponse(
                            "This video cannot be downloaded even with cookies or is restricted.", status=403
                        )

                # Serve the downloaded file
                if os.path.exists(filename):
                    response = FileResponse(open(filename, 'rb'))
                    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
                    return response
                else:
                    return HttpResponse("Error: File not found after download.", status=500)

            finally:
                # Clean up temporary cookies file
                if os.path.exists(cookies_file_path):
                    os.remove(cookies_file_path)

    else:
        form = YouTubeForm()

    return render(request, "yd.html", {'form': form})
    

def share(request):
    return render(request, "fileshare.html")

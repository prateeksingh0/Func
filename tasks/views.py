# views.py
from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse
from .forms import YouTubeForm
import yt_dlp
import os, tempfile, requests


def home(request):
    return render(request, "home.html")

def yd(request):
    if request.method == "POST":
        form = YouTubeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            download_type = form.cleaned_data['download_type']  # "audio" or "video"

            # Optional cookies
            cookies_content = os.getenv("YTDLP_COOKIES")
            cookies_file_path = None
            if cookies_content:
                tmp_cookie_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
                tmp_cookie_file.write(cookies_content)
                tmp_cookie_file.close()
                cookies_file_path = tmp_cookie_file.name

            # Use single-file format
            if download_type == 'audio':
                ydl_format = 'bestaudio[ext=m4a]'
            else:
                ydl_format = 'best[ext=mp4]'  # video+audio in one MP4 file

            ydl_opts = {
                'format': ydl_format,
                'quiet': True,
                'noplaylist': True
            }
            if cookies_file_path:
                ydl_opts['cookiefile'] = cookies_file_path

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                    media_url = info.get('url')
                    if not media_url:
                        return HttpResponse("Cannot fetch media URL. Try a different format.", status=400)

                    ext = info.get('ext', 'mp4')
                    content_type = f'audio/{ext}' if download_type=='audio' else f'video/{ext}'

                    # Stream generator
                    def stream_generator(url):
                        with requests.get(url, stream=True) as r:
                            r.raise_for_status()
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:
                                    yield chunk

                    response = StreamingHttpResponse(stream_generator(media_url), content_type=content_type)
                    response['Content-Disposition'] = f'attachment; filename="{info.get("title")}.{ext}"'
                    return response

            except yt_dlp.utils.ExtractorError:
                return HttpResponse("Requested format not available.", status=400)
            except yt_dlp.utils.DownloadError:
                return HttpResponse("Video cannot be accessed or is restricted.", status=403)
            finally:
                if cookies_file_path and os.path.exists(cookies_file_path):
                    os.remove(cookies_file_path)

    else:
        form = YouTubeForm()

    return render(request, "yd.html", {'form': form})
    

def share(request):
    return render(request, "fileshare.html")

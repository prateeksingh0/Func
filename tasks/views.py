# views.py
from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from .forms import YouTubeForm
import yt_dlp
import os, tempfile



def home(request):
    return render(request, "home.html")

def yd(request):
    if request.method == "POST":
        form = YouTubeForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            download_type = form.cleaned_data['download_type']


            cookies_content = os.getenv("YTDLP_COOKIES")
            cookies_file_path = None
            if cookies_content:
                tmp_cookie_file = tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8')
                tmp_cookie_file.write(cookies_content)
                tmp_cookie_file.close()
                cookies_file_path = tmp_cookie_file.name

            # Temporary file path
            with tempfile.TemporaryDirectory() as tmpdirname:
                file_path = os.path.join(tmpdirname, "%(title)s.%(ext)s")

            
            ydl_opts = {
                'format': 'bestaudio/best' if download_type == "audio" else 'best',
                'outtmpl': file_path,
                'cookiefile':cookies_file_path,
            }
            try: 
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)

                # Serve file as download
                if os.path.exists(filename):
                    file = open(filename, 'rb')
                    response = FileResponse(file)
                    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
                    
                    return response
                else:
                    return HttpResponse("Error: File not found.")
                
            finally:
                if cookies_file_path and os.path.exists(cookies_file_path):
                    os.remove(cookies_file_path)
    else:
        form = YouTubeForm()

    return render(request, "yd.html", {'form': form})
    

def share(request):
    return render(request, "fileshare.html")

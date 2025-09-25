# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, HttpResponse
from .forms import YouTubeForm
import yt_dlp
import os, tempfile
import zipfile
from io import BytesIO
from django.core.files.base import ContentFile
from .models import *
from .forms import *


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
    


def create_session(request):
    session = FileSession.objects.create()
    return render(request, "session_created.html", {"session": session})

def upload_files_to_session(request, session_id):
    session = get_object_or_404(FileSession, id=session_id)
    if request.method == "POST":
        uploaded_files = request.FILES.getlist("files")
        folder_files = request.FILES.getlist("folder_files")

        if folder_files:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for f in folder_files:
                    zip_file.writestr(f.name, f.read())
            zip_filename = f"session_{session.id}.zip"
            zip_content = ContentFile(zip_buffer.getvalue(), zip_filename)
            SharedFile.objects.create(session=session, file=zip_content)

        for f in uploaded_files:
            SharedFile.objects.create(session=session, file=f)

        return redirect("session_detail", session_id=session.id)

    return render(request, "upload_files.html", {"session": session})

def add_files(request, session_id):
    session = get_object_or_404(FileSession, id=session_id)

    if request.method == "POST":
        # Get list of uploaded files
        files = request.FILES.getlist("files")
        for f in files:
            SharedFile.objects.create(session=session, file=f)

        # Get list of folder files (if any)
        folder_files = request.FILES.getlist("folder_files")
        for f in folder_files:
            SharedFile.objects.create(session=session, file=f)

        # Redirect back to the same session
        return redirect("session_detail", session_id=session.id)

    # GET request: render the same upload form
    return render(request, "upload_files.html", {"session": session})


def session_detail(request, session_id):
    try:
        session = FileSession.objects.get(id=session_id)
    except FileSession.DoesNotExist:
        return redirect("share")

    files = session.files.all()

    if not files.exists():
        return redirect("share")

    return render(request, "session_detail.html", {"session": session})

# Download a single file
def download_file(request, file_id):
    f_obj = get_object_or_404(SharedFile, id=file_id)
    file_path = f_obj.file.path
    filename = os.path.basename(file_path)

    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)

    f_obj.is_downloaded = True
    f_obj.save()

    try:
        f_obj.session.refresh_from_db()
        return response  
    except FileSession.DoesNotExist:
        return redirect("share")

# Download all files as zip
def download_all_files(request, session_id):
    session = get_object_or_404(FileSession, id=session_id)
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for f in session.files.all():
            with open(f.file.path, 'rb') as file_data:
                zip_file.writestr(os.path.basename(f.file.name), file_data.read())

    for f in session.files.all():
        if os.path.exists(f.file.path):
            os.remove(f.file.path)
        f.delete()
    session.delete()

    zip_buffer.seek(0)
    response = FileResponse(zip_buffer, as_attachment=True, filename=f'Session_{session.otp}.zip')
    return response

# Delete a single file
def delete_file(request, file_id):
    f_obj = get_object_or_404(SharedFile, id=file_id)
    session_id = f_obj.session.id  

    if hasattr(f_obj, 'delete_file'):
        f_obj.delete_file()  

    if FileSession.objects.filter(id=session_id).exists():
        return redirect("session_detail", session_id=session_id)
    else:
        return redirect("share")
    

# Delete whole session
def delete_session(request, session_id):
    try:
        session = FileSession.objects.get(id=session_id)
    except FileSession.DoesNotExist:
        return redirect("share")

    for f in list(session.files.all()): 
        if f.file and os.path.exists(f.file.path):
            os.remove(f.file.path)
        f.delete()

    session.delete()

    return redirect("share")

def enter_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        try:
            session = FileSession.objects.get(otp=otp)
            if session.is_valid():
                return redirect("session_detail", session_id=session.id)
            else:
                return HttpResponse("Session expired or empty.")
        except FileSession.DoesNotExist:
            return HttpResponse("Invalid OTP")
    return render(request, "enter_otp.html")

def share(request):
    return render(request, "fileshare.html")

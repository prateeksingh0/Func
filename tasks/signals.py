# your_app/signals.py
import os
from django.core.signals import request_finished
from django.dispatch import receiver
from django.conf import settings

@receiver(request_finished)
def delete_file(sender, **kwargs):
    # This function will delete the file after the response is sent
    file_path = getattr(settings, 'YT_DOWNLOAD_FILE_PATH', None)
    
    if file_path and os.path.exists(file_path):
        os.remove(file_path)

from django.db import models
import random, os
from django.utils import timezone
from datetime import timedelta


# Create your models here.

def generates_unique_opt():
    from .models import FileSession
    otp = None
    while otp is None or FileSession.objects.filter(otp=otp).exists():
        otp = str(random.randint(100000, 999999))

    return otp

class FileSession(models.Model):
    otp = models.CharField(max_length=6, unique=True, default=generates_unique_opt)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)  # auto expiry 10 min
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() < self.expires_at and self.files.exists()

    def delete_session(self):
        for f in self.files.all():
            f.delete_file()
        self.delete()

class SharedFile(models.Model):
    session = models.ForeignKey(FileSession, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to="shared_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_downloaded = models.BooleanField(default=False)

    def delete_file(self):
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        self.delete()
        if not self.session.files.exists():
            self.session.delete()

    def filename(self):
        return os.path.basename(self.file.name)  # only file name
    
    def __str__(self):
        return self.filename()
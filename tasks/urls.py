from django.urls import path
from .views import *

urlpatterns = [
    path('',home,name = "home"),
    path('yd/',yd,name = "yd"),
    path('share/',share,name = "share"),
    path('create_session/', create_session, name="create_session"),
    path('upload/<int:session_id>/', upload_files_to_session, name="upload_files_to_session"),
    path('session/<int:session_id>/', session_detail, name="session_detail"),
    path("session/<int:session_id>/add/", add_files, name="add_files"),
    path('download/<int:file_id>/', download_file, name="download_file"),
    path('download_all/<int:session_id>/', download_all_files, name="download_all_files"),
    path('delete_file/<int:file_id>/', delete_file, name="delete_file"),
    path('delete_session/<int:session_id>/', delete_session, name="delete_session"),
    path('enter_otp/', enter_otp, name="enter_otp")
]
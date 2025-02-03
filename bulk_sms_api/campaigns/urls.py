from django.urls import path, re_path
from . import views

urlpatterns = [
    path("upload-csv/", views.upload_csv, name="upload_csv"),
    re_path(r'^send-emails(?:/(?P<group_id>\d+))?/$', views.send_emails, name="send_emails"),
    path("list-groups/", views.list_groups, name="list_groups"),
]
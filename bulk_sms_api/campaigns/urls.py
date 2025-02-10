from django.urls import path
from .views import TokenObtainPairView, TokenRefreshView, user_profile, index
from . import views

urlpatterns = [
    path('', index, name='index'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user-profile/', user_profile, name='user_profile'),
    path("upload-csv/", views.upload_csv, name="upload_csv"),
    path("send-emails/", views.send_emails, name="send_emails"), 
    path("list-groups/", views.list_groups, name="list_groups"),
]
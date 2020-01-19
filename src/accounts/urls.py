from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from accounts.views import UserProfileDetailView, UserProfileUpdateView

app_name = 'accounts'

urlpatterns = [
    path('<username>/', UserProfileDetailView.as_view(), name='detail'),
    path('<username>/update/', UserProfileUpdateView.as_view(), name='update'),
]

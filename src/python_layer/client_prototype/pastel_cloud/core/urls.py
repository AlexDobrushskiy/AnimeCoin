from django.conf.urls import url
from django.urls import include

from core.api.v1.core import UserProfileView
from core.api.v1.router import router

urlpatterns = [
    url(r'^user_profile/$', UserProfileView.as_view()),
    url(r'', include(router.urls)),
]

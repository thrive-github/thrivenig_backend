from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static



admin.site.site_header = "Thrivenig Superadmin"
admin.site.site_title = "Thrivenig Superadmin Portal"
admin.site.index_title = "Welcome to Thrivenig Superadmin Portal"




urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include('base.urls')),
    path("", include('demo.urls')),
]


# Retrieve images from /media/
urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

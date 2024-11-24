from django.contrib import admin
from django.urls import path, include
from admin import urls as admin_urls
from store import urls as store_urls
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(store_urls)),
    path('admin_panel/', include(admin_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

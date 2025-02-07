"""ventapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

from applications.getdata import views
from applications.fandesign import views


# fmt: off
# (Skip Black formatting in this section)
urlpatterns = [
    # NOTE: change the URL for Admin, for added security.
    # See #2 here: https://opensource.com/article/18/1/10-tips-making-django-admin-more-secure
    path("admin/", admin.site.urls),
    path("", include('applications.home.urls')),
    path("sysInput", TemplateView.as_view(template_name="system.html"), name="system"),
    path('', include('applications.getdata.urls')),
    path('', include('applications.fandesign.urls')),
    path('', include('applications.fanreal.urls')),
    path('', include('applications.currentstatus.urls')),
    path('', include('applications.settings.urls')),
    path('', include('applications.newproject.urls')),
    path('', include('applications.dbs.urls')),
    path('api-auth/', include('rest_framework.urls')),
]

# fmt: on


if settings.DEBUG:
    # Serve media files in development server.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

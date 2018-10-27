"""mcod URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from mcod.datasets.views import DatasetAutocomplete, getResource, getChartData

from mcod.organizations.views import OrganizationAutocomplete

admin.site.site_header = "Otwarte Dane"
admin.site.site_title = "Otwarte Dane"
admin.site.index_title = "Otwarte Dane"

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('nested_admin/', include('nested_admin.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('getResource/<int:id>/', getResource),
    path('getChartData/<int:id>/', getChartData),
]

urlpatterns += (
    path(
        'organization-autocomplete/',
        OrganizationAutocomplete.as_view(),
        name='organization-autocomplete',
    ),
    path(
        'dataset-autocomplete/',
        DatasetAutocomplete.as_view(),
        name='dataset-autocomplete',
    ),
    path('', admin.site.urls, name='admin'),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

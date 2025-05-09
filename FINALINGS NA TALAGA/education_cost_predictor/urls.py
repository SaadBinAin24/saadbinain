from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('predictor.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('predictor/', RedirectView.as_view(url='/', permanent=True)),
] 
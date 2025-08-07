from django.contrib import admin
from django.urls import path, re_path
from django.http import HttpResponse

def unauthorized_view(request):
    return HttpResponse('Unauthorized', status=401)

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^.*$', unauthorized_view),
]

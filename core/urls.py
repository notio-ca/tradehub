from django.contrib import admin
from django.urls import path, re_path
from django.http import HttpResponse
import folio.views

def unauthorized_view(request):
    return HttpResponse('Unauthorized', status=401)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("folio", folio.views.folio, name="folio"),
    re_path(r'^.*$', unauthorized_view),
]

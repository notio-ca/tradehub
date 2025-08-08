from django.shortcuts import render

def folio(request):
    return render(request, "folio/folio.html", {"data": ""})

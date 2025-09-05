from django.http import HttpResponse
from django.utils.html import escape


def index(request):
    html = (
        "<html><body>"
        "<h2>Cookie Chaos Django (Django parsing only)</h2>"
        "<p><a href='/set-host?name=__Host-name&value=Carlos'>Set __Host-name host-only</a></p>"
        "<p><a href='/reflect'>Reflect cookie value</a></p>"
        "<p><a href='/static/attacker.html'>Open attacker gadget</a></p>"
        "</body></html>"
    )
    return HttpResponse(html)


def set_host(request):
    name = request.GET.get('name', '__Host-name')
    value = request.GET.get('value', 'Carlos')
    resp = HttpResponse(f"Set host-only cookie {escape(name)}={escape(value)} at path /")
    # Host-only: do not set Domain
    resp.set_cookie(name, value, path='/', httponly=True, secure=False, samesite=None)
    return resp


def reflect(request):
    target = request.GET.get('target', '__Host-name')
    raw_header = request.META.get('HTTP_COOKIE', '')

    # Rely ONLY on Django's parsing behavior
    value = request.COOKIES.get(target)

    body = (
        f"<h3>Reflect (Django parsed)</h3>"
        f"<p>Raw Cookie header: <code>{escape(raw_header)}</code></p>"
        f"<p>Django request.COOKIES[{escape(target)}]: <b>{escape(value or '')}</b></p>"
        f"<p>All request.COOKIES: <code>{escape(str(request.COOKIES))}</code></p>"
    )
    return HttpResponse(f"<html><body>{body}</body></html>")



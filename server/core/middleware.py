import hashlib
from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from .models import LoginBucket

class LoginThrottle:
    """Limites compartilhados entre workers; buckets não armazenam usuário/IP em claro."""
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        if request.method == "POST" and request.path in ("/login/", "/admin/login/"):
            now = timezone.now()
            address = request.META.get("REMOTE_ADDR", "unknown")
            if getattr(settings, "TRUST_PROXY", False):
                address = request.META.get("HTTP_X_REAL_IP", address)
            keys = [("ip:" + address, 40),
                    ("user:" + request.POST.get("username", "").strip().casefold(), 10)]
            for raw, limit in keys:
                digest = hashlib.sha256(raw.encode()).hexdigest()
                with transaction.atomic():
                    bucket, _ = LoginBucket.objects.get_or_create(key=digest, defaults={"started_at": now})
                    bucket = LoginBucket.objects.select_for_update().get(pk=digest)
                    if now - bucket.started_at >= timedelta(minutes=15):
                        bucket.started_at, bucket.attempts = now, 0
                    if bucket.attempts >= limit:
                        response = HttpResponse("Muitas tentativas. Aguarde 15 minutos e tente novamente.", status=429, content_type="text/plain; charset=utf-8")
                        response["Retry-After"] = "900"
                        return response
                    bucket.attempts += 1
                    bucket.save()
        return self.get_response(request)

class SecurityHeaders:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        response = self.get_response(request)
        if not request.path.startswith("/admin/"):
            response["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        if request.user.is_authenticated or request.path.startswith("/login"):
            response["Cache-Control"] = "no-store"
        return response

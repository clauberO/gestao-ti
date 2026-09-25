from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import LoginBucket

class Command(BaseCommand):
    help = "Remove contadores de login expirados, sem apagar auditoria."
    def handle(self, *args, **kwargs):
        count, _ = LoginBucket.objects.filter(started_at__lt=timezone.now()-timedelta(days=1)).delete()
        self.stdout.write(f"{count} contadores expirados removidos.")

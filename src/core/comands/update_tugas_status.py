import datetime
from django.core.management.base import BaseCommand
from posts.models import Assignment
import pytz
from django.utils import timezone

now_utc = timezone.now()
tz_indonesia = pytz.timezone('Asia/Jakarta')
now_indonesia = now_utc.astimezone(tz_indonesia)

class Command(BaseCommand):
    help = 'Update status tugas jika sudah melebihi batas waktu'

    def handle(self, *args, **kwargs):
        expired_tugas = Assignment.objects.filter(due_date__lt=now_indonesia, status=Assignment.onprogress)
        for tugas in expired_tugas:
            tugas.status = Assignment.completed
            tugas.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully updated status for {expired_tugas.count()} tasks'))

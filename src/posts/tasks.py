from celery import shared_task
from posts.models import Assignment
import pytz
from django.utils import timezone

@shared_task
def update_tugas_status():
    now_utc = timezone.now()
    tz_indonesia = pytz.timezone('Asia/Jakarta')
    now_indonesia = now_utc.astimezone(tz_indonesia)
    expired_tugas = Assignment.objects.filter(due_date__lt=now_indonesia, status=Assignment.onprogress)
    for tugas in expired_tugas:
        tugas.status = Assignment.completed
        tugas.save()

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from posts.models import Assignment
import pytz
from django.utils import timezone

now_utc = timezone.now()
tz_indonesia = pytz.timezone('Asia/Jakarta')
now_indonesia = now_utc.astimezone(tz_indonesia)
@receiver(post_save, sender=Assignment)
def update_tugas_status(sender, instance, **kwargs):
    if instance.due_date < now_indonesia and instance.status != Assignment.completed:
        instance.status = Assignment.completed
        instance.save()

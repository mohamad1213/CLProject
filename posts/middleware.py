from posts.models import Assignment
import pytz
from django.utils import timezone

class UpdateTugasStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now_utc = timezone.now()
        tz_indonesia = pytz.timezone('Asia/Jakarta')
        now_indonesia = now_utc.astimezone(tz_indonesia)
        expired_tugas = Assignment.objects.filter(due_date__lt=now_indonesia, status=Assignment.onprogress)
        for tugas in expired_tugas:
            tugas.status = Assignment.completed
            tugas.save()

        response = self.get_response(request)
        return response

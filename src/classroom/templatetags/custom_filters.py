from django import template
from datetime import datetime
import pytz

register = template.Library()

@register.filter
def format_to_wib(date_str):
    try:
        # Parsing tanggal dan waktu dari string
        date_time_obj = datetime.strptime(date_str, "%B %d, %Y, %I:%M %p")
        
        # Menentukan zona waktu UTC
        utc_zone = pytz.timezone('UTC')
        
        # Menentukan zona waktu WIB (UTC+7)
        wib_zone = pytz.timezone('Asia/Jakarta')
        
        # Menambahkan zona waktu UTC ke objek datetime
        date_time_obj_utc = utc_zone.localize(date_time_obj)
        
        # Mengonversi ke zona waktu WIB
        date_time_obj_wib = date_time_obj_utc.astimezone(wib_zone)
        
        # Memformat tanggal dan waktu ke format yang diinginkan
        formatted_date_time = date_time_obj_wib.strftime("%d %B %Y, %H:%M WIB")
        
        return formatted_date_time
    except Exception as e:
        return str(e)

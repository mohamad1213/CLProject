from django.db import models
from django.contrib.auth.models import User 
from classroom.models import Classroom
from PIL import Image
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.models import AbstractUser, Permission
# Create your models here.

def user_profile_pic_path(instance, filename):
    return f'users/profile_pics/{instance.user.username}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    image = models.ImageField(default = 'users/profile_pics/default.png', upload_to=user_profile_pic_path)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

        img = Image.open(self.image.path)
        
        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE, DO_NOTHING, PROTECT
from django.conf import settings

class common(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modify_at = models.DateTimeField(auto_now=True)
    created_by= models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_created_by_user',on_delete=models.DO_NOTHING)
    modify_by= models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_modify_by_user',on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True

class User(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        if self.email:
            return self.email
        return self.username

    def get_full_name(self):
        if self.first_name and self.last_name:
            return "{} {}".format(self.first_name,self.last_name)
        else:
            return self.username
        


from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField


class Profile(models.Model):
    REGISTRATION_NORMAL = 'N'
    REGISTRATION_TWITTER = 'T'
    REGISTRATION_FACEBOOK = 'F'
    REGISTRATION_GOOGLE = 'G'

    REGISTRATION_CHOICES = [
        (REGISTRATION_NORMAL, 'Normal'),
        (REGISTRATION_FACEBOOK,'Facebook'),
        (REGISTRATION_GOOGLE, 'Google'),
        (REGISTRATION_TWITTER,'Twitter')

    ]
    fb_token = models.CharField(max_length=1000,null=True,blank=True)
    twitter_token = models.CharField(max_length=1000,null=True,blank=True)
    google_token = models.CharField(max_length=1000,null=True,blank=True)
    registration_method = models.CharField(
        max_length=1, choices=REGISTRATION_CHOICES, default=REGISTRATION_NORMAL)
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.user.username
        
    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)
    
    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

class Address(models.Model):
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = CountryField()
    postcode = models.CharField(max_length=45)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modify_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField()
    

class common(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modify_at = models.DateTimeField(auto_now=True)
    created_by= models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_created_by_user',on_delete=models.DO_NOTHING)
    modify_by= models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_modify_by_user',on_delete=models.DO_NOTHING)

    class Meta:
        abstract = True


class contact_us(common):
    name = models.CharField(max_length=45)
    email = models.CharField(max_length=45)
    contact_no = models.CharField(max_length=10)
    message = models.TextField()
    note_admin = models.TextField(null=True,blank=True)









    







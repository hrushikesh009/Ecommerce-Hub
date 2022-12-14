from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.db import models


class common(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modify_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='%(class)s_created_by_user', on_delete=models.DO_NOTHING)
    modify_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='%(class)s_modify_by_user', on_delete=models.DO_NOTHING)
    active = models.BooleanField()

    class Meta:
        abstract = True


class configuration(common):
    conf_key = models.CharField(max_length=45)
    conf_value = models.CharField(max_length=45)


class EmailTemplate(common):
    title = models.CharField(max_length=45)
    subject = models.CharField(max_length=255)
    content = models.TextField()


class CMS(FlatPage, common):
    meta_title = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    meta_keywords = models.TextField(null=True, blank=True)


class Banner(common):
    banner_path = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.banner_path


class Banner_images(common):
    banner = models.ForeignKey(Banner, on_delete=models.CASCADE)
    image_name = models.CharField(max_length=100)
    image = models.ImageField()

    def __str__(self):
        return self.image_name

from django.contrib import admin
from custom_admin.forms import CMSForm
from . import models


admin.site.register(models.configuration)


@admin.register(models.CMS)
class CMSAdmin(admin.ModelAdmin):
    form = CMSForm
    fieldsets = (
        (None, {'fields': ('url', 'title', 'content', 'meta_title',
         'meta_description', 'meta_keywords', 'created_by', 'modify_by', 'sites')}),
        (('Advanced options'), {
            'classes': ('collapse',),
            'fields': (
                'enable_comments',
                'registration_required',
                'template_name',
            ),
        }),
    )

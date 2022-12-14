from django.forms import ModelForm
from .models import EmailTemplate, CMS, Banner, configuration
from django import forms
from django.contrib.flatpages.forms import FlatpageForm
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext, gettext_lazy as _


class ConfigForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = configuration
        fields = ['conf_key', 'conf_value', 'active']

        widgets = {
            'conf_key': forms.TextInput(attrs={'class': 'form-control'}),
            'conf_value': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CMSForm(FlatpageForm):
    required_css_class = 'required'

    class Meta:
        model = CMS
        fields = ['url', 'title', 'content', 'meta_title',
                  'meta_description', 'meta_keywords', 'sites', 'active']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control required'}),
            'url': forms.TextInput(attrs={'class': 'form-control required'}),
            'content': forms.Textarea(attrs={'class': 'form-control required', 'id': 'summernote'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_keywords': forms.TextInput(attrs={'class': 'form-control'}),

        }


class EmailTemplateForm(ModelForm):

    required_css_class = 'required'

    class Meta:
        model = EmailTemplate
        fields = ['title', 'subject', 'content', 'active']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control required'}),
            'subject': forms.TextInput(attrs={'class': 'form-control required'}),
            'content': forms.Textarea(attrs={'class': 'form-control required', 'id': 'summernote'}),

        }


class BannerForm(ModelForm):
    required_css_class = 'required'
    banner_path = forms.RegexField(
        label=_("Banner_path"),
        max_length=100,
        regex=r'^[-\w/\.~]+$',
        help_text=_(
            'Example: “/about/contact/”. Make sure to have leading and trailing slashes.'),
        error_messages={
            "invalid": _(
                "This value must contain only letters, numbers, dots, "
                "underscores, dashes, slashes or tildes."
            ),
        },
    )

    class Meta:
        model = Banner
        fields = ['banner_path', 'active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self._trailing_slash_required():
            self.fields['banner_path'].help_text = _(
                'Example: “/about/contact”. Make sure to have a leading slash.'
            )

    def _trailing_slash_required(self):
        return (
            settings.APPEND_SLASH and
            'django.middleware.common.CommonMiddleware' in settings.MIDDLEWARE
        )

    def clean_banner_path(self):
        url = self.cleaned_data['banner_path']
        if not url.startswith('/'):
            raise ValidationError(
                gettext("URL is missing a leading slash."),
                code='missing_leading_slash',
            )
        if self._trailing_slash_required() and not url.endswith('/'):
            raise ValidationError(
                gettext("URL is missing a trailing slash."),
                code='missing_trailing_slash',
            )
        return url

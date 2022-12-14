from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from custom_admin.models import EmailTemplate
import logging
import os

logger = logging.getLogger('django')
dir_path =os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path,'templates/default_email_template.html')



def mail(*args,**kwargs):
    try:
        htmly =  EmailTemplate.objects.get(id = kwargs['id'])

        open(filename,'w').close()
        file = open(filename,'w')
        file.write(htmly.content)
        file.close()
        html_content = render_to_string(filename,kwargs['context'])
        text_content = strip_tags(html_content)
        send_mail(
            htmly.subject,
            text_content,
            settings.EMAIL_HOST_USER,
            kwargs['user_email'],
            html_message = html_content,
            fail_silently=False
        )
        logger.info('Email was sent Successfully!')
    except Exception as e:
        logger.error(e)

def check_categorys_children(category_queryset,*args,**kwargs):
    try:
        a = []
        a.append(category_queryset.id)
        if category_queryset.children.exists():
            for child in category_queryset.children.all():
                a.append(child.id)
        return a
    except Exception as e:
        logger.error(e)




import logging
from Product.models import WishList
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
import os

logger = logging.getLogger('django')
dir_path =os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path,'templates/user_wishlist.html')

logger = logging.getLogger('django')

def my_cron():
    try:
        admin_users = Group.objects.get(name='admin').user_set.all()
        customer = Group.objects.get(name='Customer').user_set.all()
        for user in customer:
            user_wishlist = WishList.objects.select_related('user').prefetch_related('wishitems__product').get(user__username=user.username)
            if user_wishlist.wishitems.all().count() > 0:
                try:
                    html_content = render_to_string(filename,{'wishlist':user_wishlist})
                    text_content = strip_tags(html_content)
                    send_mail(
                        'HEY ADMIN! CHECKOUT THE USERS WISHLIST',
                        text_content,
                        settings.EMAIL_HOST_USER,
                        [users.email for users in admin_users],
                        html_message = html_content,
                        fail_silently=False
                    )
                    logger.info('Email was sent Successfully!')
                except Exception as e:
                    logger.error(e)
    except Exception as e:
        logger.error(e)
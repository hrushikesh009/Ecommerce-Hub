from django.contrib.auth.models import Group
from store.models import Profile
from User.models import User


def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'facebook':
        try:
            profile = Profile.objects.filter(user=user.id)
            profile.update(
                fb_token = response.get('access_token'),
                registration_method = 'F'
            )
        except Exception as e:
            profile = Profile()
            profile.user = User(pk=user.id)
            profile.fb_token = response.get('access_token')
            profile.registration_method = 'F'
            profile.save()
        
            
        group = Group.objects.get(name='customer')
        group.user_set.add(user)
    if backend.name == 'google-oauth2':
        try:
            profile = Profile.objects.filter(user=user.id)
            profile.update(
                google_token = response.get('access_token'),
                registration_method = 'G'
            )
        except Exception as e:
            profile = Profile()
            profile.user = User(pk=user.id)
            profile.google_token = response.get('access_token')
            profile.registration_method = 'G'
            profile.save()

            
        group = Group.objects.get(name='customer')
        group.user_set.add(user)
    if backend.name == 'twitter':
        try:
            profile = Profile.objects.filter(user=user.id)
            profile.update(
                twitter_token = response.get('access_token'),
                registration_method = 'T'
            )
        except Exception as e:
            profile = Profile()
            profile.user = User(pk=user.id)
            profile.twitter_token = response.get('access_token')
            profile.registration_method = 'T'
            profile.save()
        
            
        group = Group.objects.get(name='customer')
        group.user_set.add(user)

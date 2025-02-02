from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from myapp.models import Profile  # Replace `myapp` with your app's name

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

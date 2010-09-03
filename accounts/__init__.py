# Callback after a user object is saved
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from accounts.views import user_post_save_callback

post_save.connect(user_post_save_callback, sender=User)
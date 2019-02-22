from django.contrib.auth.models import AbstractUser
from django.db import models


# Custom User model to simplify adding new field in future
class User(AbstractUser):
    def save(self, *args, **kwargs):
        is_new = self.id is None
        super(User, self).save(*args, **kwargs)
        if is_new:
            self.profile = UserProfile.objects.create(user=self)


class UserProfile(models.Model):
    short_bio = models.TextField(blank=True)
    picture = models.ImageField(null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return '{} profile'.format(self.user.username)

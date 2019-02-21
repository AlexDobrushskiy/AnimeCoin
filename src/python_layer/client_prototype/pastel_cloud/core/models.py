from django.contrib.auth.models import AbstractUser
from django.db import models


# Custom User model to simplify adding new field in future
class User(AbstractUser):
    pass


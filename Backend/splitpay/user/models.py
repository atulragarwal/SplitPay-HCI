from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
import datetime
from django.utils.translation import ugettext_lazy as _
from .managers import UserManager

class User(AbstractBaseUser):

    username = None
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=10, unique=True)
    balance = models.IntegerField(default=0)
    profile_pic = models.ImageField(upload_to="profile_pic")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ 'phone_number','name','balance','profile_pic' ]

    objects = UserManager()

    def __str__(self):
        return self.email

from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _

class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, name, phone_number, profile_pic, password=None):
        user = self.model(
            email=self.normalize_email(email),
            phone_number=phone_number,
            name=name,
            profile_pic=profile_pic,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, name, phone_number, profile_pic, password):
        user = self.create_user(
            email,
            password=password,
            phone_number=phone_number,         
            name=name,
            profile_pic=profile_pic,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone_number, profile_pic, password):
        user = self.create_user(
            email,
            password=password,
            phone_number=phone_number,
            name= "True",
            profile_pic=profile_pic,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user
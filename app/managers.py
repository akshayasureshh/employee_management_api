from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _



class CustomUserManager(BaseUserManager):
    def create_user(self, **fields):
        if not (fields.get('email')):
            raise ValueError(_('Email must be set'))
        if not (fields.get('first_name') and fields.get('last_name')):
            raise ValueError(_('First name & last name is required'))
        if fields.get('email'):
            if not fields.get('password'):
                raise ValueError(_('Password is required when email is provided'))
            fields['email'] = self.normalize_email(fields['email'])  
        user = self.model(**fields)
        if fields.get('password'):
            user.set_password(fields.get('password'))
        user.save()

        return user

    def create_superuser(self, **fields):
        fields.setdefault('is_staff', True)
        fields.setdefault('is_superuser', True)
        fields.setdefault('is_active', True)
        if fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(**fields)

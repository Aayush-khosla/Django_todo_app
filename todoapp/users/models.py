from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from users import constants as users_constants
from todoapp.managers import SoftDeleteManager 


class UserManager(BaseUserManager):
    """
    Add manager methods here to create user and super user
    """

    def create_user(self, email, first_name, last_name, password, **extra_fields):
        if not email:
            raise ValidationError(users_constants.USER_EMAIL_HELPER)
        if not password:
            raise ValidationError(users_constants.USER_PASSWORD_HELPER)

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name,
                        last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True
        return self.create_user(email, first_name, last_name, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Needed fields
    - first_name (max_length=30)
    - last_name (max_length=150)
    - email (should be unique)
    - password (already inherited from AbstractBaseUser; encrypt password before saving to database)
    - last_login (already inherited from AbstractBaseUser)
    - is_superuser
    - first_name (max_length=30)
    - email (should be unique)
    - is_staff
    - date_joined (default should be time of object creation)
    - last_name (max_length=150)
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    first_name = models.CharField(max_length=users_constants.FIRST_NAME_LIMIT, help_text=users_constants.FIRST_NAME_HELP_TEXT)
    last_name = models.CharField(max_length=users_constants.LAST_NAME_LIMIT, help_text=users_constants.LAST_NAME_HELP_TEXT)
    email = models.EmailField(unique=True, help_text=users_constants.EMAIL_HELP_TEXT)
    is_staff = models.BooleanField(default=False, help_text=users_constants.IS_STAFF_HELP_TEXT)
    is_superuser = models.BooleanField(default=False, help_text=users_constants.IS_SUPERUSER_HELP_TEXT)
    date_joined = models.DateTimeField(default=timezone.now, help_text=users_constants.DATE_JOINED_HELP_TEXT)
    deleted = models.BooleanField(default=False, help_text=users_constants.HELP_TEXT_DELETE)

    objects = UserManager()
    active_objects = SoftDeleteManager() 

    def __str__(self) :
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def delete(self, using=None, keep_parents=False):
        """ Soft delete user and mark related Todos as deleted """
        self.deleted = True
        self.save()

        self.todos.update(deleted=True)

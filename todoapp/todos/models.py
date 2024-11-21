from django.conf import settings
from django.db import models

from todos import constants as todos_constants
from todoapp.managers import SoftDeleteManager


class Todo(models.Model):
    """
        Needed fields
        - user (fk to User Model - Use AUTH_USER_MODEL from django.conf.settings)
        - name (max_length=1000)
        - done (boolean with default been false)
        - date_created (with default of creation time)
        - date_completed (set it when done is marked true)
        - deleted (boolean to mark soft delete )
        Add string representation for this model with todos name.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, help_text=todos_constants.HELP_TEXT_USER)
    name = models.CharField(max_length=todos_constants.MAX_LENGTH_TODO_NAME, help_text=todos_constants.HELP_TEXT_NAME)
    done = models.BooleanField(default=False, help_text=todos_constants.HELP_TEXT_DONE)
    date_created = models.DateTimeField(auto_now_add=True, help_text=todos_constants.HELP_TEXT_DATE_CREATED)
    date_completed = models.DateTimeField(null=True, blank=True, help_text=todos_constants.HELP_TEXT_DATE_COMPLETED)
    deleted = models.BooleanField(default=False, help_text=todos_constants.HELP_TEXT_DELETE)

    objects = SoftDeleteManager()

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        """ Soft delete by setting deleted to True """
        self.deleted = True
        self.save()


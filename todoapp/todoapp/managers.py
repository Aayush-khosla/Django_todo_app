from django.db import models

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        """ Return only objects that are not deleted. """
        return super().get_queryset().filter(deleted=False)

    def all_with_deleted(self):
        """ Return all objects including soft deleted ones. """
        return super().get_queryset()

    def delete(self):
        """ Soft delete method to update the deleted field. """
        self.deleted = True
        self.save()

from django.contrib import admin

from users import models as users_models

admin.site.register(users_models.CustomUser)

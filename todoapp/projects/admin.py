from django.contrib import admin

from projects import models as projects_models

admin.site.register(projects_models.Project)
admin.site.register(projects_models.ProjectMember)

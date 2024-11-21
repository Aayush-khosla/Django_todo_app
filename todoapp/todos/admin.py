from django.contrib import admin

from todos import models as todos_models 

class TodoAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "done", "date_created")
    list_filter = ("done", "date_created")
    def get_queryset(self, request):
        """Override get_queryset to return all todos, including soft deleted ones."""
        return todos_models.Todo.objects.all_with_deleted()


admin.site.register(todos_models.Todo, TodoAdmin)

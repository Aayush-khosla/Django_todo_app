from rest_framework import(
    pagination as rest_framework_pagination,
    viewsets as rest_framework_viewsets
)

from todos import (
    constants as todos_constants,
    models as todos_models,
    serializers as todos_serializers
)


class TodoPagination(rest_framework_pagination.PageNumberPagination):
    page_size = todos_constants.PAGE_SIZE
    page_size_query_param = 'page_size'


class TodoAPIViewSet(rest_framework_viewsets.ModelViewSet):
    """
        success response for create/update/get
        {
          "name": "",
          "done": true/false,
          "date_created": ""
        }

        success response for list
        [
          {
            "name": "",
            "done": true/false,
            "date_created": ""
          }
        ]
    """
    pagination_class = TodoPagination
    serializer_class = todos_serializers.TodoListSerializer

    def get_queryset(self):
        return todos_models.Todo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

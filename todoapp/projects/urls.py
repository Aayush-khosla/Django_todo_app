from django.urls import path

from projects import views as projects_views

urlpatterns = [
    path('<int:project_id>/members/add', projects_views.ProjectMemberApiViewSet.as_view({'post':'add_members'}), name='add_project_members'),
    path('<int:project_id>/members/remove', projects_views.ProjectMemberApiViewSet.as_view({'post':'remove_members'}), name='remove_project_members')
]

from django.db.models import Count, Exists, OuterRef, BooleanField
from django.shortcuts import get_object_or_404

from rest_framework import (
    permissions as rest_framework_permissions,
    response as rest_framework_response,
    status as rest_framework_status,
    viewsets as rest_framework_viewsets
)

from projects import(
    constants as projects_constants,
    models as projects_models,
    serializers as projects_serializers
)
from users import models as users_models


class ProjectMemberApiViewSet(rest_framework_viewsets.ViewSet):
    """
       constraints
        - a user can be a member of max 2 projects only
        - a project can have at max N members defined in database for each project
       functionalities
       - add users to projects

       Functionalities
       - Add users to projects
         Request
         { user_ids: [1,2,...n] }
         Response
         {
           logs: {
             <user_id>: <status messages>
           }
         }
         following are the possible status messages
         case1: if user is added successfully then - "Member added Successfully"
         case2: if user is already a member then - "User is already a Member"
         case3: if user is already added to 2 projects - "Cannot add as User is a member in two projects"
         case4: if user not found - "User not found"

       - Update to remove users from projects
         Request
         { user_ids: [1,2,...n] }
         Response
         {
           logs: {
             <user_id>: <status messages>
           }
         }

         URL for this view - projects/<int:project_id>/members/add     post
                           - projects/<int:project_id>/members/remove  post
    """

    permission_classes=(rest_framework_permissions.IsAdminUser,)

    def get_project(self, project_id):
        """Retrieve the project based on the provided project ID."""
        return get_object_or_404(projects_models.Project.objects.annotate(
            member_count=Count('projectmember')
        ), id=project_id)

    def get_users(self, user_ids, project_id):
        """Fetch users based on provided user IDs."""
        if not user_ids:
            return rest_framework_response.Response(
             {"error": projects_constants.USER_IDS_EMPTY}, status=rest_framework_status.HTTP_400_BAD_REQUEST
          )
        try:
            user_ids = [int(user_id) for user_id in user_ids]
        except (ValueError, TypeError):
          return rest_framework_response.Response(
             {"error": projects_constants.USER_IDS_ERROR}, status=rest_framework_status.HTTP_400_BAD_REQUEST
          )

        is_member = projects_models.ProjectMember.objects.filter(
            project_id=project_id, member_id=OuterRef('id')
        )
        return users_models.CustomUser.objects.filter(id__in=user_ids).annotate(
            project_count=Count('projectmember'),
            is_in_project=Exists(is_member, output_field=BooleanField())
        ).values('id', 'project_count', 'is_in_project')

    def add_members(self, request, project_id):
        project = self.get_project(project_id)
        user_ids = request.data.get('user_ids', [])
        users = self.get_users(user_ids, project_id)
        if isinstance(users, rest_framework_response.Response): 
          return users

        serializer = projects_serializers.AddMemberSerializer(
            data=request.data, context={'project': project, 'users': users}
        )
        if serializer.is_valid():
            serializer.save()
            return rest_framework_response.Response(serializer.data, status=rest_framework_status.HTTP_200_OK)

    def remove_members(self, request, project_id):
        project = self.get_project(project_id)
        user_ids = request.data.get('user_ids', [])
        users = self.get_users(user_ids, project_id)

        if isinstance(users, rest_framework_response.Response): 
          return users

        serializer = projects_serializers.RemoveMemberSerializer(
            data=request.data, context={'project': project, 'users':users}
        )
        if serializer.is_valid():
            serializer.save()
            return rest_framework_response.Response(serializer.data, status=rest_framework_status.HTTP_200_OK)

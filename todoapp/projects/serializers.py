from rest_framework import serializers as rest_serializers

from projects import(
    constants as projects_constants,
    models as projects_models
)
from users import serializers as users_serializers

class ProjectSerializer(rest_serializers.ModelSerializer):
    status = rest_serializers.CharField(source='get_status_display', read_only=True)
    existing_member_count = rest_serializers.IntegerField(read_only=True)

    class Meta:
        model = projects_models.Project
        fields = ('id', 'name', 'status', 'existing_member_count', 'max_members')


class ProjectNamesSerializer(rest_serializers.ModelSerializer):
    project_name =rest_serializers.CharField(source='name', read_only=True)
    done = rest_serializers.SerializerMethodField()

    class Meta: 
        model = projects_models.Project
        fields = ('project_name', 'done', 'max_members')

    def get_done(self ,obj):
        return obj.status == projects_models.Project.COMPLETED


class ProjectReportSerializer(rest_serializers.Serializer):
    project_title = rest_serializers.CharField()
    report = users_serializers.UserTodoStatsWithoutIdSerializer(many=True)


class UserProjectSerializer(rest_serializers.Serializer):
    first_name = rest_serializers.CharField()
    last_name = rest_serializers.CharField()
    email = rest_serializers.EmailField()
    to_do_projects = rest_serializers.ListField(child=rest_serializers.CharField())
    in_progress_projects = rest_serializers.ListField(child=rest_serializers.CharField())
    completed_projects = rest_serializers.ListField(child=rest_serializers.CharField())

class BaseProjectMemberSerializer(rest_serializers.Serializer):
    user_ids = rest_serializers.ListField(
        child=rest_serializers.IntegerField(), write_only=True
    )
    logs = rest_serializers.DictField(read_only=True)

    def validate(self, data):
        """Perform custom validation, logs will  this must the ibbe handled in child serializers."""
        user_ids = data.get('user_ids')
        users = self.context.get('users')

        found_user_ids = {user['id'] for user in users}
        missing_user_ids = set(user_ids) - found_user_ids

        logs = {user_id: projects_constants.USER_DOES_NOT_EXIST for user_id in missing_user_ids}
        data["logs"] = logs
        return data


class AddMemberSerializer(BaseProjectMemberSerializer):
    def validate(self, data):
        """Perform validation specific to adding members."""
        data = super().validate(data)
        users = self.context.get('users')
        project = self.context.get('project')
        logs = data["logs"]

        current_member_count = project.member_count

        for user in users:
            user_id = user['id']
            if user['is_in_project']:
                logs[user_id] = projects_constants.ALREADY_MEMBER           
            elif user['project_count'] >= 2:
                logs[user_id] = projects_constants.ALREADY_IN_TWO_PROJECTS
            elif current_member_count >= project.max_members:
                logs[user_id] = projects_constants.MEMBER_LIMIT_REACHED
            else:
                logs[user_id] = projects_constants.MEMBER_ADDED
                current_member_count += 1 

        data["logs"] = logs
        return data

    def save(self):
        """Add members to the project."""
        user_ids = self.validated_data["user_ids"]
        project = self.context.get('project')

        members_to_add = [
            projects_models.ProjectMember(member_id=user_id, project=project)
            for user_id in user_ids
            if self.validated_data["logs"].get(user_id) == projects_constants.MEMBER_ADDED
        ]
        projects_models.ProjectMember.objects.bulk_create(members_to_add)


class RemoveMemberSerializer(BaseProjectMemberSerializer):
    def validate(self, data):
        """Perform validation specific to removing members."""
        data = super().validate(data)
        users = self.context.get('users')
        logs = data["logs"]

        for user in users:
            user_id = user['id']
            if not user['is_in_project']:
                logs[user_id] = projects_constants.NOT_A_MEMBER
            else:
                logs[user_id] = projects_constants.MEMBER_REMOVED

        data["logs"] = logs
        return data

    def save(self):
        """Remove members from the project."""
        user_ids = self.validated_data["user_ids"]
        project = self.context.get('project')

        projects_models.ProjectMember.objects.filter(
            member_id__in=user_ids, project=project
        ).delete()

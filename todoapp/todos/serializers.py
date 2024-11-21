from django.contrib.auth import get_user_model
from rest_framework import serializers as rest_serializers

from todos import models as todos_models
from users import serializers as users_serializers


class BaseTodoSerializer(rest_serializers.ModelSerializer):
    status = rest_serializers.SerializerMethodField()
    created_at = rest_serializers.SerializerMethodField()

    class Meta:
        model = todos_models.Todo
        fields = ('id', 'name', 'status', 'created_at')

    def get_status(self, obj):
        return "Done" if obj.done else "To Do"

    def get_created_at(self, obj):
        return obj.date_created.strftime("%I:%M %p, %d %b, %Y")


class TodoSerializer(BaseTodoSerializer):
    creator = users_serializers.CustomUserSerializer(source='user')

    class Meta(BaseTodoSerializer.Meta):
        fields = BaseTodoSerializer.Meta.fields + ('creator',)


class TodoDateRangeSerializer(BaseTodoSerializer):
    creator = rest_serializers.ReadOnlyField(source='user.get_full_name')
    email = rest_serializers.EmailField(source='user.email')

    class Meta(BaseTodoSerializer.Meta):
        fields =BaseTodoSerializer.Meta.fields +('creator', 'email')


class TodoListSerializer(rest_serializers.ModelSerializer):

    class Meta:
        model = todos_models.Todo
        fields = ('id', 'name', 'done', 'date_created')



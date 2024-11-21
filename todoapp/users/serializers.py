from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers as rest_serializers
from rest_framework.authtoken.models import Token

from users import constants as users_constants

# Add your rest_serializers
User = get_user_model()


class UserSerializer(rest_serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


class CustomUserSerializer(rest_serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class UserToPendingBaseSerializer(rest_serializers.ModelSerializer):
    pending_count = rest_serializers.IntegerField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'pending_count')


class UserTodoPendingSerializer(UserToPendingBaseSerializer):

    class Meta(UserToPendingBaseSerializer.Meta):
        fields = UserToPendingBaseSerializer.Meta.fields + ('id',)


class UserTodoStatsWithoutIdSerializer(UserToPendingBaseSerializer):
    completed_count = rest_serializers.IntegerField()

    class Meta(UserToPendingBaseSerializer.Meta):
        fields = UserToPendingBaseSerializer.Meta.fields + ('completed_count',)


class UserTodoStatsSerializer(UserTodoStatsWithoutIdSerializer):

    class Meta(UserTodoStatsWithoutIdSerializer.Meta):
        fields = UserTodoStatsWithoutIdSerializer.Meta.fields + ('id',)


class UserRegistrationSerializer(rest_serializers.ModelSerializer):
    password = rest_serializers.CharField(write_only=True, trim_whitespace=False)
    confirm_password = rest_serializers.CharField(write_only=True, trim_whitespace=False)
    token = rest_serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 
                  'password', 'confirm_password', 'date_joined', 'token')
        read_only_fields = ('token' , 'date_joined')

    def validate_email(self, email):
        if User.active_objects.filter(email=email).exists():
            raise rest_serializers.ValidationError(users_constants.EMAIL_VALIDATION_MESSAGE)
        return email

    def validate(self, validated_data):
        if validated_data['confirm_password'] != validated_data['password'] :
            raise rest_serializers.ValidationError(users_constants.PASSWORD_FIELD_MESSAGE)
        validated_data['password'] = make_password(validated_data['password'])
        validated_data.pop('confirm_password')
        return validated_data

    def get_token(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        return token.key


class UserLoginSeralizer(rest_serializers.ModelSerializer):
    email = rest_serializers.EmailField(write_only=True)
    password = rest_serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ('email', 'password')

    def validate(self, data):
        user = authenticate(request=self.context.get('request'), username=data.get('email'), password=data.get('password'))
        if user is None or hasattr(user, 'deleted') and user.deleted:
            raise rest_serializers.ValidationError(users_constants.INVALID_PASSWORD_MESSAGE)

        data['user'] = user
        return data

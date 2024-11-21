from rest_framework import (
    generics as rest_framework_generics,
    permissions as rest_framework_permissions,
)
from rest_framework.authtoken import views

from users import serializers as users_serializers 


class UserRegistrationAPIView(rest_framework_generics.CreateAPIView):
    """
        success response format
         {
           first_name: "",
           last_name: "",
           email: "",
           date_joined: "",
           "token"
         }
    """
    permission_classes = (rest_framework_permissions.AllowAny,)
    serializer_class = users_serializers.UserRegistrationSerializer


class UserLoginAPIView(views.ObtainAuthToken):
    """
        success response format
         {
           auth_token: ""
         }
    """
    permission_classes = (rest_framework_permissions.AllowAny, )
    serializer_class = users_serializers.UserLoginSeralizer

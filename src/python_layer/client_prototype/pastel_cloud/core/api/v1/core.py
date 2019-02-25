from rest_framework import serializers
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from core.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('short_bio', 'picture',)


# curl example of picture upload:
# curl -X PUT -S -H 'Accept: application/json' -H 'Authorization: Token <Token>' -F "picture=@<path to local file>" -F "short_bio=some_short_bio here" 127.0.0.1:8000/api/v1/user_profile/
class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

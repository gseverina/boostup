from rest_framework import serializers
from boostup_app.models import HubSpotUser


class HubSpotUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = HubSpotUser
        fields = ('id',
                  'userid',
                  'access_token',
                  'refresh_token')

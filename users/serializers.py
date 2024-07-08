from rest_framework import serializers
from .models import User, Organisation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'email', 'phone','password']
        extra_kwargs = {
            'password': {'write_only' : True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
 
class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ['orgId', "name", 'description']


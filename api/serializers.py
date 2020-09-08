import logging

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import Block, Message

activity_log = logging.getLogger('activity')

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ['id', 'user', 'blocked_user']

class UserSerializer(serializers.ModelSerializer):
    blocked_users = BlockSerializer(many = True, required = False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'blocked_users']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    # Yeni kullanıcı olustur
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        activity_log.info("User {} is created.".format(user.username))
        return user

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'message', 'sender_user', 'recipient_user', 'created_at', 'delivered_at', 'read_at')

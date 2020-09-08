import logging

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.views import ObtainAuthToken

from api.models import Message

activity_log = logging.getLogger('activity')

class CustomAuthTokenSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Username"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                # log eklendi.
                activity_log.warning("Login failed for {}.".format(username))
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class CustomTokenView(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        # log eklendi.
        try: 
           username = request.data['username']
           password = request.data['password']
        except:
            activity_log.warning("Login failed for {} (Missing field).".format(request.data.get('username', 'empty user')))

        response = super(CustomTokenView, self).post(request, *args, **kwargs)

        # Login olanan kullanıcının yeni mesajı varsa iletildi tarihi eklenecek.
        user = User.objects.get(username=username)
        messages = Message.objects.filter(recipient_user=user, delivered_at=None)
        for message in messages:
            message_to_be_delivered = Message.objects.get(id=message.id)
            message_to_be_delivered.delivered_at = timezone.now()
            message_to_be_delivered.save()

        # log eklendi.
        activity_log.info("{} logged in".format(request.data['username']))
        return response

custom_token_view = CustomTokenView.as_view()

import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


class RegisterUserTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="user_test2", password="user_test")

    # Yeni kullanıcı
    def test_registration(self):
        data = {
            "username": "user_test",
            "password": "user_test"
        }
        response = self.client.post("/api/v1/user/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # Var olan kullanıcı
    def test_registration_invalid(self):
        data = {
            "username": "user_test2",
            "password": "user_test2"
        }
        response = self.client.post("/api/v1/user/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SendMessageTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="message_test_user", password="message_test_user")
        self.user2 = User.objects.create_user(username="to_message_user", password="to_message_user")

        self.token = Token.objects.create(user=self.user)
        self.api_auth()

    def api_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + str(self.token))

    # Mesaj at
    def test_send_message(self):
        data = {
            "recipient_username": "to_message_user",
            "message": "test ok"
        }
        response = self.client.post("/api/v1/message/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
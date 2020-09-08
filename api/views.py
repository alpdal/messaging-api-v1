import datetime
import logging

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Block, Message
from .pagination import CustomPagination
from .serializers import BlockSerializer, MessageSerializer, UserSerializer

activity_log = logging.getLogger('activity')

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer    
    permission_classes = (AllowAny, )
    http_method_names = ['post']

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    pagination_class = CustomPagination
    http_method_names = ['post', 'get']

    # Mesaj at
    def create(self, request, *args, **kwargs):
        sender_user = request.user

        # Gerekli alanlar dolu mu?
        if 'recipient_username' in request.data and 'message' in request.data:
            message = request.data['message']
            recipient_username = request.data['recipient_username']

            # Kullanıcı mevcut mu?
            try:
                recipient_user = User.objects.get(username=recipient_username)
                is_blockage_exists = Block.objects.filter(user=recipient_user, blocked_user=sender_user).exists()

                # Bloklanan kullanıcı mesaj atamıyor.
                if is_blockage_exists:
                    response = {'error': 'Message not sent, you are blocked by user'}
                    activity_log.info("User {} made bad attempt sending message to {}.".format(sender_user.username, recipient_username))
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

                # Kullanıcı kendine mesaj gönderemiyor.
                elif recipient_user == sender_user:
                    response = {'error': 'You can not send message to yourself'}
                    activity_log.info("User {} made bad attempt sending message to {}.".format(sender_user.username, recipient_username))
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)                        

                else:
                    message = Message.objects.create(message=message, sender_user=sender_user, recipient_user=recipient_user)
                    serializer = MessageSerializer(message)
                    response = {
                            'status': 'Message is sent',
                            'data': serializer.data
                        }
                    activity_log.info("User {} sent message to {}.".format(sender_user.username, recipient_username))
                    return Response(response, status=status.HTTP_200_OK)
                    

            except:
                response = {'error': 'Message not sent, there is no such user'}
                activity_log.info("User {} made bad attempt sending message to {}.".format(sender_user.username, recipient_username))
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        else:
            response = {'status': 'Message not sent, you have to obtain recipient username and message',
                        'recipient_username': 'This field is required.',
                        'message': 'This field is required.'
                    }
            activity_log.info("User {} made bad attempt sending message.".format(sender_user.username))
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    # Mesajları görüntüle
    def list(self, request, *args, **kwargs):
        combined_queryset =  Message.objects.filter(sender_user=request.user) |  Message.objects.filter(recipient_user=request.user)
        params = ['from_user', 'to_user', 'to_date', 'from_date']

        # Bütün parametreler opsiyonel oldugu tek tek deneniyor.
        for param in params:
            try: 
                if param == 'from_user':
                    user = User.objects.get(username=request.query_params.get(param))
                    combined_queryset = combined_queryset.filter(sender_user=user)
                elif param == 'to_user':
                    user = User.objects.get(username=request.query_params.get(param))
                    combined_queryset = combined_queryset.filter(recipient_user=user)
                elif param == 'to_date':
                    date = models.DateField().to_python(request.query_params.get('to_date'))
                    # gün sonuna gitmek için 24 sa eklendi.
                    date += datetime.timedelta(1)
                    combined_queryset = combined_queryset.filter(created_at__lte=date)
                else:
                    date = models.DateField().to_python(request.query_params.get('from_date'))
                    combined_queryset = combined_queryset.filter(created_at__gte=date)
            except:
                pass
        
        # Mesajları olusturulma tarihine göre sırala ve sayfalandır.
        queryset = combined_queryset.order_by('created_at')
        page = self.paginate_queryset(queryset)

        # Sayfa yoksa devam et.
        if page is not None:

            # Görüntülenen mesajları kayıt altına al.
            messages_viewed_str = ""
            for i in range(len(page)):
                messages_viewed_str += str(page[i].id) + ' '
                
                # İlk defa acılan mesaj varsa okunma tarihi ekle.
                if page[i].recipient_user == request.user and page[i].read_at is None:
                    message_to_be_read = Message.objects.get(id=page[i].id)
                    message_to_be_read.read_at = timezone.now()
                    message_to_be_read.save()
                    page[i] = message_to_be_read
            
            # Görüntülenen mesajları logla.
            activity_log.info("User {} viewed messages with ids {}.".format(request.user.username, messages_viewed_str))
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Görüntülenen mesajları kayıt altına al.
        messages_viewed_str = ""
        for i in range(len(queryset)):
            messages_viewed_str += str(queryset[i].id) + ' '
            
            # İlk defa acılan mesaj varsa okunma tarihi ekle.
            if queryset[i].recipient_user == request.user and queryset[i].read_at is None:
                message_to_be_read = Message.objects.get(id=queryset[i].id)
                message_to_be_read.read_at = timezone.now()
                message_to_be_read.save()
                queryset[i] = message_to_be_read
        
        # Görüntülenen mesajları logla.
        activity_log.info("User {} viewed messages with ids {}.".format(request.user.username, messages_viewed_str))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class BlockViewSet(viewsets.ModelViewSet):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    http_method_names = ['post']

    # Kullanıcı blokla
    def create(self, request, *args, **kwargs):
        user = request.user

        # Gerekli alan dolu mu?
        if 'block_user' in request.data:
            block_username = request.data['block_user']

            # Kullanıcı mevcut mu?
            try:
                block_user = User.objects.get(username=block_username)
                is_blockage_exists = Block.objects.filter(user=user, blocked_user=block_user).exists()

                # Bloke mevcut mu?
                if is_blockage_exists:
                    response = {'error': 'Blockage exists, cannot be created again'}
                    activity_log.info("User {} made bad attempt to block {}.".format(user.username, block_username))
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)

                # Kullanıcı kendini bloklayamaz.
                elif block_user == user:
                    response = {'error': 'You cannot block yourself'}
                    activity_log.info("User {} made bad attempt to block {}.".format(user.username, block_username))
                    return Response(response, status=status.HTTP_400_BAD_REQUEST)
                    
                else:
                    block = Block.objects.create(user=user, blocked_user=block_user)
                    serializer = BlockSerializer(block)
                    response = {
                            'message': 'Blockage is created',
                            'data': serializer.data
                        }
                    activity_log.info("User {} blocked {}.".format(user.username, block_username))
                    return Response(response, status=status.HTTP_200_OK)
                    
            except:
                response = {'error': 'There is no such user'}
                activity_log.info("User {} made bad attempt to block {}.".format(user.username, block_username))
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        else:
            response = {'block_user': 'This field is required.'}
            activity_log.info("User {} made bad attempt to block.".format(user.username))
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

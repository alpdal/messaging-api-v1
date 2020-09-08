from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    message = models.TextField(max_length=360, blank=True)
    # kullanıcılardan birinin silinmesi durumunda mesaj nesnesi de silinecek.
    sender_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_user')
    recipient_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient_user')
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True, editable=False)
    delivered_at = models.DateTimeField(null=True, blank=True, editable=False)

    def __str__(self):
        return "{} ({} to {})".format(self.message[:40], self.sender_user, self.recipient_user)

class Block(models.Model):
    # kullanıcılardan birinin silinmesi durumunda bloke nesnesi de silinecek.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_users', blank=True, null=True)
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return "{} blocks {} ({})".format(self.user, self.blocked_user, self.id)
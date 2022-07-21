from django.db import models
from django.contrib.auth.models import AbstractUser

class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default = True, db_index = True, verbose_name = 'Has been activated ?')
    send_messages = models.BooleanField(default = True, verbose_name = 'Send update messages ?')
    
    class Meta(AbstractUser.Meta):
        pass

#class Person(models.Model):
#    name = models.CharField(max_length=20)
#    age = models.IntegerField()



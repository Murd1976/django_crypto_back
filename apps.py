from django.apps import AppConfig
from django.dispatch import Signal
from .utilities import send_activation_notification

user_registered = Signal()

def user_registered_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])
    
user_registered.connect(user_registered_dispatcher)



class Crypto_backConfig(AppConfig):
    name = 'crypto_back'
    verbose_name = 'Crypto back testing.'




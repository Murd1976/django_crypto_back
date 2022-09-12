from django.db import models
from django.contrib.auth.models import AbstractUser

class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default = True, db_index = True, verbose_name = 'Has been activated ?')
    send_messages = models.BooleanField(default = True, verbose_name = 'Send update messages ?')
    paid_account = models.BooleanField(default = False)
    
    class Meta(AbstractUser.Meta):
        pass

class AllBackTests(models.Model	):
    strategy_name = models.CharField(max_length=50, verbose_name='Strategy.')
    owner = models.ForeignKey(AdvUser, verbose_name='Test owner.', on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Test data.')
    
    parts = minimal_roi1_time = models.IntegerField(verbose_name="Pairs part")
    minimal_roi1_time = models.IntegerField()
    minimal_roi1_value = models.DecimalField(max_digits=2, decimal_places=1)
    minimal_roi2_time = models.IntegerField()
    minimal_roi2_value = models.DecimalField(max_digits=2, decimal_places=1)
    minimal_roi3_time = models.IntegerField()
    minimal_roi3_value = models.DecimalField(max_digits=2, decimal_places=1)
    minimal_roi4_time = models.IntegerField()
    minimal_roi4_value = models.DecimalField(max_digits=2, decimal_places=1)
    arg_N =  models.IntegerField(verbose_name="Series length (N)")
    arg_R =  models.IntegerField(verbose_name="Persen of same candles (R)")
    arg_P =  models.IntegerField(verbose_name="Price incriase in N candles (P)")
    arg_MR =  models.DecimalField(max_digits=2, decimal_places=1, verbose_name="Movement ROI (MR)")
    stoploss = models.DecimalField(max_digits=2, decimal_places=1, verbose_name="Stop-loss (after 0 min)")
    my_stoploss_time = models.IntegerField(verbose_name="My Stop-loss (after [n] min)")
    my_stoploss_value = models.DecimalField(max_digits=2, decimal_places=1, verbose_name="My Stop-loss (after [n] min)")
    arg_stoploss =  models.DecimalField(max_digits=2, decimal_places=1, verbose_name="Dsired Stop-loss value (S)")
    text_log = models.TextField(verbose_name="Loggin text")
    
    class Meta():
        verbose_name_plural = "BackTest settings"
        verbose_name = "BackTest settings"
        ordering = ['-created_at']

class DataBufer(models.Model):
    name = models.CharField(max_length=20)
    user_strategy_choise = models.IntegerField()

    def __str__(self):
        """
        String for representing the MyModelName object (in Admin site etc.)
        """
        return '%s:%d' %(self.name, self.user_strategy_choise)
#        return '%s (%s)' % (self.name, self.user_strategy_choise)

    def delete_everything(self):
        DataBufer.objects.all().delete()
    
#class Person(models.Model):
#    name = models.CharField(max_length=20)
#    age = models.IntegerField()



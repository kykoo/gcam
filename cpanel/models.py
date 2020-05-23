from django.db import models

# Create your models here.

class Acc1(models.Model):
    measure_time = models.CharField(max_length=16,null=False)
    rmsACC = models.FloatField()
    fileUploaded = models.BooleanField(default=False)

class Acc2(models.Model):
    measure_time = models.CharField(max_length=16,null=False)
    rmsACC = models.FloatField()
    fileUploaded = models.BooleanField(default=False)
    
class Acc3(models.Model):
    measure_time = models.CharField(max_length=16)
    rmsACC = models.FloatField()
    fileUploaded = models.BooleanField(default=False)
    
class Event(models.Model):
    measure_time = models.CharField(max_length=16)
    

class SystemState(models.Model):
    acc_threshold = models.FloatField()
    icam = models.IntegerField()
    Time_gcUploaded_acc1 = models.DateTimeField(null=True)
    Time_gcUploaded_acc2 = models.DateTimeField(null=True)
    Time_gcUploaded_acc3 = models.DateTimeField(null=True)
    Time_gcUploaded_tmp1 = models.DateTimeField(null=True)
    Time_gcUploaded_tmp2 = models.DateTimeField(null=True)
    Time_gcUploaded_tmp3 = models.DateTimeField(null=True)



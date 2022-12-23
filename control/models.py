from django.db import models

# long, double, double, double, double
class MovePos(models.Model):
    lAxisNo = models.IntegerField()
    dPos = models.FloatField()
    dVel = models.FloatField()
    dAccel = models.FloatField()
    dDecel = models.FloatField()

class MoveVel(models.Model):
    lAxisNo = models.IntegerField()
    dVel = models.FloatField()
    dAccel = models.FloatField()
    dDecel = models.FloatField()
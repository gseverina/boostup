from django.db import models


class HubSpotUser(models.Model):
    userid = models.CharField(max_length=100, blank=False, default='')
    access_token = models.CharField(max_length=256, blank=False, default='')
    refresh_token = models.CharField(max_length=256, blank=False, default='')


class HubSpotDeal(models.Model):
    deal_id = models.IntegerField(default=0)
    name = models.CharField(max_length=100, blank=False, default='')
    stage = models.CharField(max_length=100, blank=False, default='')
    close_date = models.DateTimeField()
    amount = models.DecimalField(decimal_places=2, max_digits=8)
    type = models.CharField(max_length=100, blank=False, default='')

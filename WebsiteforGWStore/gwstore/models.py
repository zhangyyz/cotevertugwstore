""">>>>>>>For Testing: Delete Me>>>>>>>>>>>>>>
class Barcode(models.Model):
    number = models.BigIntegerField()
    image_data_uri = models.CharField(max_length=100000)
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Bill(models.Model):
    user = models.ForeignKey(User, related_name='bill_user')
    pickup_person = models.ForeignKey(User, related_name='bill_pickup_person', null=True)
    bill_number = models.BigIntegerField(unique=True)
    contain_dangerous_goods = models.CharField(max_length=10)
    sender_name = models.CharField(max_length=50)
    sender_address = models.CharField(max_length=200)
    sender_phone = models.CharField(max_length=20)
    sender_post_code = models.CharField(max_length=10)
    sender_district = models.CharField(max_length=50)
    receiver_name = models.CharField(max_length=50)
    receiver_address = models.CharField(max_length=200)
    receiver_phone = models.CharField(max_length=20)
    receiver_post_code = models.CharField(max_length=10)
    buy_package_lost_insurance = models.CharField(max_length=10)
    package_lost_insured_amount = models.FloatField(null=True, blank=True)
    package_lost_premium_amount = models.FloatField(null=True, blank=True)
    item_1_description = models.CharField(max_length=30)
    item_1_quantity = models.IntegerField(default=0)
    item_2_description = models.CharField(max_length=30, blank=True)
    item_2_quantity = models.IntegerField(blank=True, null=True)
    item_3_description = models.CharField(max_length=30, blank=True)
    item_3_quantity = models.IntegerField(blank=True, null=True)
    item_4_description = models.CharField(max_length=30, blank=True)
    item_4_quantity = models.IntegerField(blank=True, null=True)
    item_5_description = models.CharField(max_length=30, blank=True)
    item_5_quantity = models.IntegerField(blank=True, null=True)
    weight_lb = models.DecimalField(null=True, blank=True,decimal_places=2, max_digits=16)
    creation_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    pickup_time = models.DateTimeField(null=True)
    client_signature_data_uri = models.CharField(max_length=1048576, null=True)  # 1M characters
    status_code = models.CharField(max_length=5)
    status_description = models.CharField(max_length=40)
    email_sent_out_time = models.DateTimeField(null=True)
    batch_excel_exported_time = models.DateTimeField(null=True)
    uuid_for_avoiding_duplicate = models.CharField(max_length=50, unique=True)

class HTMLCode(models.Model):
    for_component = models.CharField(max_length=30)
    html_code = models.TextField(max_length=52428800)  # 50M characters

class OtherInformation(models.Model):
    key = models.CharField(max_length=30)
    value = models.CharField(max_length=1048576, null=True)  # 1M characters

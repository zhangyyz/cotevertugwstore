# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('bill_number', models.BigIntegerField(unique=True)),
                ('contain_dangerous_goods', models.CharField(max_length=10)),
                ('sender_name', models.CharField(max_length=50)),
                ('sender_address', models.CharField(max_length=200)),
                ('sender_phone', models.CharField(max_length=20)),
                ('sender_post_code', models.CharField(max_length=10)),
                ('sender_district', models.CharField(max_length=50)),
                ('receiver_name', models.CharField(max_length=50)),
                ('receiver_address', models.CharField(max_length=200)),
                ('receiver_phone', models.CharField(max_length=20)),
                ('receiver_post_code', models.CharField(max_length=10)),
                ('buy_package_lost_insurance', models.CharField(max_length=10)),
                ('package_lost_insured_amount', models.FloatField(null=True, blank=True)),
                ('package_lost_premium_amount', models.FloatField(null=True, blank=True)),
                ('item_1_description', models.CharField(max_length=30)),
                ('item_1_quantity', models.IntegerField(default=0)),
                ('item_2_description', models.CharField(max_length=30, blank=True)),
                ('item_2_quantity', models.IntegerField(null=True, blank=True)),
                ('item_3_description', models.CharField(max_length=30, blank=True)),
                ('item_3_quantity', models.IntegerField(null=True, blank=True)),
                ('item_4_description', models.CharField(max_length=30, blank=True)),
                ('item_4_quantity', models.IntegerField(null=True, blank=True)),
                ('item_5_description', models.CharField(max_length=30, blank=True)),
                ('item_5_quantity', models.IntegerField(null=True, blank=True)),
                ('weight_lb', models.IntegerField(null=True, blank=True)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('pickup_time', models.DateTimeField(null=True)),
                ('client_signature_data_uri', models.CharField(null=True, max_length=1048576)),
                ('status_code', models.CharField(max_length=5)),
                ('status_description', models.CharField(max_length=40)),
                ('email_sent_out_time', models.DateTimeField(null=True)),
                ('batch_excel_exported_time', models.DateTimeField(null=True)),
                ('pickup_person', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='bill_pickup_person')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='bill_user')),
            ],
        ),
        migrations.CreateModel(
            name='HTMLCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('for_component', models.CharField(max_length=30)),
                ('html_code', models.TextField(max_length=52428800)),
            ],
        ),
        migrations.CreateModel(
            name='OtherInformation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('key', models.CharField(max_length=30)),
                ('value', models.CharField(null=True, max_length=1048576)),
            ],
        ),
    ]

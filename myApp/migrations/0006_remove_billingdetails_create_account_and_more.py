# Generated by Django 5.1.4 on 2024-12-13 11:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0005_billingdetails_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billingdetails',
            name='create_account',
        ),
        migrations.RemoveField(
            model_name='billingdetails',
            name='ship_to_different_address',
        ),
    ]

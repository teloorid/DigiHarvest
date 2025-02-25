# Generated by Django 5.1.4 on 2024-12-13 08:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myApp', '0002_produce_produceimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produce',
            name='status',
            field=models.CharField(choices=[('Planted', 'Planted'), ('Growing', 'Growing'), ('Harvested', 'Harvested'), ('Failed', 'Failed'), ('Delayed', 'Delayed')], default='Planted', max_length=20),
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='myApp.cart')),
                ('produce', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myApp.produce')),
            ],
        ),
    ]

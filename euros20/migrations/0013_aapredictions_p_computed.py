# Generated by Django 3.2.4 on 2021-06-13 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('euros20', '0012_auto_20210611_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='aapredictions',
            name='p_computed',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
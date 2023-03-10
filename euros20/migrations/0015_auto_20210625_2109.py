# Generated by Django 3.2.4 on 2021-06-25 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('euros20', '0014_auto_20210624_1335'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aamatches',
            name='endtime',
            field=models.CharField(blank=True, choices=[('Full-time', 'Full time'), ('Extra-time', 'Extra Time'), ('Penalties', 'Penalties')], default='Full-time', max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='aapredictions',
            name='p_endtime',
            field=models.CharField(blank=True, choices=[('Full-time', 'Full time'), ('Extra-time', 'Extra Time'), ('Penalties', 'Penalties')], default='Full-time', max_length=30, null=True),
        ),
    ]

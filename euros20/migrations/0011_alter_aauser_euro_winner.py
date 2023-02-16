# Generated by Django 3.2.4 on 2021-06-10 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('euros20', '0010_auto_20210610_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aauser',
            name='euro_winner',
            field=models.CharField(blank=True, choices=[(None, 'Select'), ('France', 'France - 16 pts'), ('Belgium', 'Belgium - 20 pts'), ('England', 'England - 20 pts'), ('Germany', 'Germany - 30 pts'), ('Italy', 'Italy - 30 pts'), ('Portugal', 'Portugal - 30 pts'), ('Spain', 'Spain - 30 pts'), ('Netherlands', 'Netherlands - 40 pts'), ('Croatia', 'Croatia - 50 pts'), ('Denmark', 'Denmark - 50 pts'), ('Austria', 'Austria - 100 pts'), ('Czech Republic', 'Czech Republic - 100 pts'), ('Finland', 'Finland - 100 pts'), ('Hungary', 'Hungary - 100 pts'), ('North Macedonia', 'North Macedonia - 100 pts'), ('Poland', 'Poland - 100 pts'), ('Russia', 'Russia - 100 pts'), ('Scotland', 'Scotland - 100 pts'), ('Slovakia', 'Slovakia - 100 pts'), ('Sweden', 'Sweden - 100 pts'), ('Switzerland', 'Switzerland - 100 pts'), ('Turkey', 'Turkey - 100 pts'), ('Ukraine', 'Ukraine - 100 pts'), ('Wales', 'Wales - 100 pts')], max_length=20, null=True),
        ),
    ]

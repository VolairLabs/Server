# Generated by Django 4.2.9 on 2024-10-09 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_thenotifications_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='thenotifications',
            options={'ordering': ['-date']},
        ),
        migrations.AlterField(
            model_name='thenotifications',
            name='section',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='thenotifications',
            name='type',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]

# Generated by Django 4.1.7 on 2023-05-16 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myauth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='users/avatars'),
        ),
    ]

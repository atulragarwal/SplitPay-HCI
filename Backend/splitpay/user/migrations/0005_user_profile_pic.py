# Generated by Django 3.2.3 on 2021-05-31 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_alter_user_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profile_pic',
            field=models.ImageField(default='jasdoasd.jpg', upload_to='profile_pic'),
            preserve_default=False,
        ),
    ]

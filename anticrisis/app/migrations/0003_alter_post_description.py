# Generated by Django 5.2.4 on 2025-07-25 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_post_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='description',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]

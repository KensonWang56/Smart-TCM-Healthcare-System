# Generated by Django 4.2.20 on 2025-03-22 18:03

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='用户唯一标识'),
        ),
    ]

# Generated by Django 2.2.9 on 2020-05-19 23:44

from django.db import migrations
import mdeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('book_manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summary',
            name='summary',
            field=mdeditor.fields.MDTextField(),
        ),
    ]

# Generated by Django 4.0.1 on 2022-01-08 13:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('News', '0009_remove_post_category_post_category'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='category',
            new_name='categories',
        ),
    ]
# Generated by Django 4.0.1 on 2022-01-06 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('News', '0007_rename_publishdate_post_publish_date_alter_ad_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='replied_on',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='News.comment'),
        ),
    ]

# Generated by Django 5.1.6 on 2025-03-02 15:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0016_campaign_campaign_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='content',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='campaigns.content'),
        ),
    ]

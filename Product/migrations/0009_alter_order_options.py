# Generated by Django 4.0 on 2022-07-02 17:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Product', '0008_alter_attribute_values_created_by_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-created_at']},
        ),
    ]

# Generated by Django 5.1.4 on 2025-01-09 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0009_alter_myuser_gender_alter_myuser_user_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leavesmodel',
            name='dayoption',
            field=models.CharField(choices=[('Half', 'Half'), ('Full', 'Full')], default='full', max_length=20, verbose_name='Day Option'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='gender',
            field=models.CharField(blank=True, choices=[('Female', 'Female'), ('Male', 'Male'), ('Others', 'Others')], max_length=20, verbose_name='Gender'),
        ),
    ]

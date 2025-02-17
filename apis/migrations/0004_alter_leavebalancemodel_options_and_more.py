# Generated by Django 5.1.4 on 2024-12-16 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0003_alter_attendancemodel_options_alter_myuser_gender_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='leavebalancemodel',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='leavesmodel',
            options={'ordering': ['-id']},
        ),
        migrations.AlterModelOptions(
            name='myuser',
            options={'ordering': ['-id'], 'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
        migrations.AddField(
            model_name='myuser',
            name='emp_code',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='Employee Code'),
        ),
        migrations.AlterField(
            model_name='leavesmodel',
            name='leave_type',
            field=models.CharField(choices=[('Earned', 'Earned'), ('Sick', 'Sick')], max_length=20, verbose_name='Leave Type'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='gender',
            field=models.CharField(blank=True, choices=[('Others', 'Others'), ('Female', 'Female'), ('Male', 'Male')], max_length=20, verbose_name='Gender'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='user_type',
            field=models.CharField(choices=[('User', 'User'), ('Admin', 'Admin')], default='Admin', max_length=10, verbose_name='User Type'),
        ),
    ]

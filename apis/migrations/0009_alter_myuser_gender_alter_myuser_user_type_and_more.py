# Generated by Django 5.1.4 on 2025-01-09 09:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0008_alter_myuser_gender_userdocument'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='gender',
            field=models.CharField(blank=True, choices=[('Others', 'Others'), ('Male', 'Male'), ('Female', 'Female')], max_length=20, verbose_name='Gender'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='user_type',
            field=models.CharField(choices=[('User', 'User'), ('Admin', 'Admin')], default='Admin', max_length=10, verbose_name='User Type'),
        ),
        migrations.AlterField(
            model_name='userdocument',
            name='document_type',
            field=models.CharField(blank=True, choices=[('AADHAR', 'Aadhar'), ('PAN', 'PAN'), ('MARKSHEET_10', '10th Marksheet'), ('MARKSHEET_12', '12th Marksheet'), ('GRADUATION', 'Graduation Certificate'), ('POST_GRADUATION', 'Post Graduation Certificate'), ('CHEQUE', 'Cancelled Cheque'), ('PASSBOOK', 'Passbook'), ('OFFER_LETTER', 'Offer Letter'), ('EXP_LETTER', 'Experience Letter'), ('PAYSLIP', 'Payslip')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='userdocument',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='user_documents/'),
        ),
        migrations.AlterField(
            model_name='userdocument',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to=settings.AUTH_USER_MODEL),
        ),
    ]

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models
from apis.choices import *
import uuid
import random
from Attendance.settings import *
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

class CommonTimePicker(models.Model):
    created_at = models.DateTimeField("Created Date", auto_now_add=True)
    updated_at = models.DateTimeField("Updated Date", auto_now=True)

    class Meta:
        abstract = True


class MyUserManager(BaseUserManager):

    def create_user(self, email, password):
        if not email:
            raise ValueError('Users must have an Email Address')

        user = self.model(
            email=self.normalize_email(email),
            is_active=False,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.model(email=email)
        user.set_password(password)
        user.is_superuser = True
        if user.is_superuser:
            user.first_name = "SuperAdmin"
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser,CommonTimePicker):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    user_type = models.CharField("User Type", max_length=10, default='Admin', choices=USERTYPE)
    first_name = models.CharField("First Name", max_length=256, blank=True, null=True)
    last_name = models.CharField("Last Name", max_length=256, blank=True, null=True)
    emp_code = models.CharField("Employee Code", max_length=256, blank=True, null=True,unique=True)
    email = models.EmailField("Email Address", null=True, blank=True, unique=True,db_index=True)
    phone_number = models.CharField('Phone Number', max_length=256,default="",null=True,blank=True)
    gender = models.CharField("Gender", max_length=20, choices=GENDER,blank=True)
    dob = models.DateField("Dob", blank=True, null= True)
    joining_date = models.DateField("Date of Joining", blank=True, null= True)
    designation = models.CharField("Designation", max_length=256, blank=True, null=True)
    address = models.TextField("Address",max_length=1000,blank=True,null=True)

    otp = models.CharField('OTP', max_length=4, blank=True, null=True)
    is_superuser = models.BooleanField("Super User", default=False)
    is_staff = models.BooleanField("Staff", default=False)
    is_active = models.BooleanField("Active", default=False)
    email_verify = models.BooleanField("Email Verify", default=False)
    
    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-id']

    def __str__(self):
        return f"{self.uuid}_{self.email}" 
    
    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_superuser

    def get_short_name(self):
        return self.email

    def otp_creation(self):
        otp = random.randint(1000, 9999)
        self.otp = otp
        self.save()
        return otp
    

class AttendanceModel(CommonTimePicker):
    """ Addendance model """
    attendance_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='attendance_user')

    in_time = models.DateTimeField("In Time",blank=True, null=True)
    out_time = models.DateTimeField("Out Time",blank=True, null=True)
    duration = models.CharField("Duration",max_length=100, blank=True,null=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.attendance_user.first_name} {self.in_time}"



class LeavesModel(CommonTimePicker):
    """ Leaves Model """
    leave_user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='leave_user')
    leave_type = models.CharField("Leave Type", max_length=20, choices=LEAVE_TYPE)

    from_date = models.DateField("From Date", blank=True, null=True)
    to_date = models.DateField("To Date")
    reason = models.TextField("Reason", blank=True, null=True)
    status = models.CharField("Status", max_length=20, choices=LEAVE_STATUS, default='Pending')

    approved_by = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approver')
    approved_on = models.DateTimeField("Approved On", null=True, blank=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.leave_user.first_name

    def leave_duration(self):
        """ Calculate leave duration in days """
        if self.from_date and self.to_date:
            return (self.to_date - self.from_date).days + 1
        return 0


class LeaveBalanceModel(models.Model):
    """ Leave Balance Model """
    leave_balance_user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='leave_balance_user')
    earned_leave = models.FloatField("Earned Leave", default=0)
    sick_leave = models.FloatField("Sick Leave", default=0)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.leave_balance_user.first_name



@receiver(post_save, sender=LeavesModel)
def update_leave_balance(sender, instance, **kwargs):
    """ Update leave balance when a leave is approved """
    if instance.status == 'Approved':
        leave_balance = LeaveBalanceModel.objects.filter(leave_balance_user=instance.leave_user).first()
        if leave_balance:
            leave_duration = instance.leave_duration()

            if instance.leave_type == 'Earned':
                if leave_balance.earned_leave >= leave_duration:
                    leave_balance.earned_leave -= leave_duration
                else:
                    raise ValueError("Insufficient Earned Leave balance.")
            elif instance.leave_type == 'Sick':
                if leave_balance.sick_leave >= leave_duration:
                    leave_balance.sick_leave -= leave_duration
                else:
                    raise ValueError("Insufficient Sick Leave balance.")
            leave_balance.save()



    # anouncement ===============================================================

class AnouncementModel(CommonTimePicker):
    """ Anouncement Model """
    user_anouncement = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='user_anouncement')
    title = models.CharField("Title", max_length=200, blank=True, null=True)
    desc = models.CharField("Description", max_length=200, blank=True, null=True)

    def __str__(self):
        return self.title
    
class RegularizationModel(CommonTimePicker):
    user_regularization = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='user_regularization')
    date = models.DateField("Date", blank=True, null=True)
    in_time = models.TimeField("In Time",blank=True, null=True)
    out_time = models.TimeField("Out Time",blank=True, null=True)
    reason = models.CharField("Reason", max_length=200, blank=True, null=True)
    approval = models.BooleanField("Approval", default=False)

    class Meta:
        ordering = ['-id']

    def __str__ (self):
       return f"{self.user_regularization.first_name} {self.reason}"
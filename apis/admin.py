from django.contrib import admin
from apis.models import *



@admin.register(MyUser)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ['emp_code','first_name', 'last_name', 'email', 'phone_number','gender','dob']

@admin.register(AttendanceModel)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ['attendance_user','in_time', 'out_time', 'duration']

@admin.register(LeavesModel)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ['leave_user', 'leave_type', 'dayoption', 'from_date','to_date','reason','status','approved_by','approved_on']

@admin.register(LeaveBalanceModel)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ['leave_balance_user', 'earned_leave', 'sick_leave','used_earned_leave','used_sick_leave']


@admin.register(AnouncementModel)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ['user_anouncement', 'title', 'desc']


@admin.register(RegularizationModel)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ['user_regularization', 'date', 'in_time', 'out_time','reason','approval']


@admin.register(AttendanceInOutImages)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ['image_user', 'image', 'image_type']

@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ['user', 'document_type', 'file', 'uploaded_at']


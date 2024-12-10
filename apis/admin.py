from django.contrib import admin
from apis.models import *

admin.site.register(MyUser)
admin.site.register(AttendanceModel)
admin.site.register(LeavesModel)
admin.site.register(LeaveBalanceModel)
admin.site.register(AnouncementModel)
admin.site.register(RegularizationModel)

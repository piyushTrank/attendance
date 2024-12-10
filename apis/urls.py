from django.urls import path
from apis.views import *


urlpatterns = [
    path('login/', LoginAPI.as_view(),name="login"),
    path("logout/",LogoutUserAPIView.as_view(),name='logout'),
    path('create-employee/', CreateEmployeeApi.as_view(),name="create-employee"),
    path('employee-list/', EmployeeListApi.as_view(),name="employee-list"),
    path('employee-details/', EmployeeDetailsAPi.as_view(),name="employee-details"),
    path('delete-employee/', DeleteUserAPi.as_view(),name="delete-employee"),
    path('edit-employee/', EditEmployeeApi.as_view(),name="edit-employee"),

    # anouncement ===============================================================
    path('anouncement/', AddanouncementApi.as_view(),name="anouncement"),
    path('all-anouncement/', AllanouncementApi.as_view(),name="all-anouncement"),

    # Attendance ===============================================================
    path('in-out-time/', AttendanceInOutTime.as_view(),name="in-out-time"),
    path('in-time/', InTimeAttendance.as_view(),name="in-time"),
    path('get-all-attendance/', GetAllAttendance.as_view(),name="get-all-attendance"),
    path('admin-dashboard-attendance/', AdminDashboardAttendance.as_view(),name="admin-dashboard-attendance"),

    # Regularization ============================================================
    path('apply-regularization/', RegularizationApi.as_view(),name="apply-regularization"),
    path('approve-regularization/', ApprovalRegularise.as_view(),name="approve-regularization"),
]



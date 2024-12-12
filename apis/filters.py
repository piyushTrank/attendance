from django_filters import rest_framework as filters
from apis.models import MyUser , AttendanceModel
from django.db.models import Q


class MyUserFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_combined', label='Search by name or designation')
    class Meta:
        model = MyUser
        fields = []
    def filter_combined(self, queryset, name, value):
        return queryset.filter(
            first_name__icontains=value) | queryset.filter(
            last_name__icontains=value) | queryset.filter(
            designation__icontains=value)
    


class AttendanceFilter(filters.FilterSet):
    year = filters.NumberFilter(field_name='in_time', lookup_expr='year', label='Year')
    month = filters.NumberFilter(field_name='in_time', lookup_expr='month', label='Month')
    class Meta:
        model = AttendanceModel
        fields = ['year', 'month']



# class AttendanceView(filters.FilterSet):
#     from_date = filters.DateFilter(field_name='in_time', lookup_expr='gte', label='From Date')
#     to_date = filters.DateFilter(field_name='in_time', lookup_expr='lte', label='To Date')
#     name = filters.CharFilter(method='filter_by_name', label='Search by Name')

#     class Meta:
#         model = AttendanceModel
#         fields = ['from_date', 'to_date', 'name']

#     def filter_by_name(self, queryset, name, value):
#         return queryset.filter(
#             Q(attendance_user__first_name__icontains=value) | 
#             Q(attendance_user__last_name__icontains=value)
#         )

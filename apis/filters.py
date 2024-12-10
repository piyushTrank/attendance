from django_filters import rest_framework as filters
from apis.models import MyUser

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

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apis.models import *
from rest_framework.exceptions import APIException
from apis.serializer import *
from rest_framework.permissions import AllowAny, IsAuthenticated
from apis.pagination import *
from apis.filters import *
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.db.models import F, Count, Q
import calendar
from calendar import monthrange




class LoginAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            user = MyUser.objects.get(email=request.data.get("email"))
            if user.user_type == "SuperAdmin":
                return Response({"success": False, "message": "Invalid user type."}, status=status.HTTP_400_BAD_REQUEST)
            if user.is_active == False:
                return Response({"success": False, "message": "Inactive user type."}, status=status.HTTP_400_BAD_REQUEST)


        except MyUser.DoesNotExist:
            return Response({"message": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        refresh = RefreshToken.for_user(user)
        token = {
            'access': str(refresh.access_token),
        }
        return Response({
            'responsecode': status.HTTP_200_OK,
            'userid': user.uuid,
            'user_type':user.user_type,
            'token': token,
            'responsemessage': 'logged in successfully.'
        }, status=status.HTTP_200_OK)



class CreateEmployeeApi(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            token = {'access': str(refresh.access_token)}
            response = {
                "responsecode": status.HTTP_201_CREATED,
                "responsemessage": "User created successfully.",
                "userid": user.uuid,
                'user_type':user.user_type,
                "token": token
            }
            return Response(response, status=status.HTTP_201_CREATED)
        
        # Format error messages
        error_messages = {field: errors[0] for field, errors in serializer.errors.items()}
        response = {
            "code": status.HTTP_400_BAD_REQUEST,
            "message": error_messages
        }
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
    



class LogoutUserAPIView(APIView):
    def post(self, request):
        return Response({"success": True, "message": "Logout user successfully"}, status=status.HTTP_200_OK)
    




class EmployeeListApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_filter = MyUserFilter(
            request.query_params,
            queryset=MyUser.objects.filter(user_type="User", is_active=True)
        )
        if not user_filter.is_valid():
            return Response({"code": 400, "message": user_filter.errors}, status=400)
        filtered_queryset = user_filter.qs.order_by("-id").values(
            'uuid', 'first_name', 'last_name', 'email', 'phone_number',
            'gender', 'dob', 'joining_date', 'designation', 'address'
        )
        paginator = StandardResultsSetPagination()
        paginated_queryset = paginator.paginate_queryset(filtered_queryset, request, view=self)
        return paginator.get_paginated_response(paginated_queryset)




class EmployeeDetailsAPi(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        uuid = request.query_params.get("uuid")  
        if not uuid:
            return Response({"message": "UUID parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = MyUser.objects.get(uuid=uuid)
            user_data = {
                'uuid': user.uuid,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone_number': user.phone_number,
                'gender': user.gender,
                'dob': user.dob,
                'joining_date': user.joining_date,
                'designation': user.designation,
                'address': user.address,
            }
            return Response(
                {"message": "User data retrieved successfully", "data": user_data},
                status=status.HTTP_200_OK
            )
        except MyUser.DoesNotExist:
            return Response(
                {"message": "User with the provided UUID does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
        
class DeleteUserAPi(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request):
        uuid = request.query_params.get("uuid") 
        if not uuid:
            return Response({"message": "UUID parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        user = MyUser.objects.get(uuid=uuid)
        user.delete()
        return Response({"code":status.HTTP_200_OK,"message":"User deleted sucessfully."},status=status.HTTP_200_OK)
    



class AddanouncementApi(APIView):
    def post(self, request):
        anouncement = AnouncementModel.objects.create(
            user_anouncement=request.user,
            title=request.data['title'],
            desc=request.data['desc']
        )
        return Response({"code":status.HTTP_200_OK,"message":"Anouncement added sucessfully."},status=status.HTTP_200_OK)
    


class AllanouncementApi(APIView):
    def get(self, request):
        try:
            announcements = AnouncementModel.objects.values("id", "title", "desc", "created_at").order_by("-id")
            paginator = StandardResultsSetPagination()
            paginated_queryset = paginator.paginate_queryset(announcements, request, view=self)
            return paginator.get_paginated_response(paginated_queryset)
        except Exception as e:
            return Response({"message": str(e), "code": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)



class EditEmployeeApi(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            user = MyUser.objects.get(uuid=request.query_params.get("uuid"), is_active=True)
        except MyUser.DoesNotExist:
            return Response(
                {"code": 404, "message": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Partially update the user
        serializer = EmployeeUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "code": status.HTTP_200_OK,
                    "message": "User updated successfully.",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        error_messages = {field: errors[0] for field, errors in serializer.errors.items()}
        return Response(
            {"code": status.HTTP_400_BAD_REQUEST, "message": error_messages},
            status=status.HTTP_400_BAD_REQUEST
        )
    


from django.utils.timezone import now, make_aware


class AttendanceInOutTime(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user_uuid = request.data.get('uuid')
        if user_uuid:
            try:
                user = MyUser.objects.get(uuid=user_uuid)  
            except MyUser.DoesNotExist:
                return Response({"error": "User with the given UUID does not exist."}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user

        
        in_time_str = request.data.get("in_time", "").strip()
        out_time_str = request.data.get("out_time", "").strip()
        in_time = now()
        out_time = None

        today_start = make_aware(datetime.combine(in_time.date(), datetime.min.time()))
        today_end = make_aware(datetime.combine(in_time.date(), datetime.max.time()))
        attendance = AttendanceModel.objects.filter(
            attendance_user=user,
            in_time__range=(today_start, today_end)
        ).first()

        if attendance:
            if out_time_str.lower() == "out_time" or not out_time_str:
                out_time = now()  
            else:
                try:
                    out_time = make_aware(datetime.fromisoformat(out_time_str))
                except ValueError:
                    return Response(
                        {"error": "Invalid out_time format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            # Update `out_time` and calculate duration
            attendance.out_time = out_time
            attendance.duration = str(attendance.out_time - attendance.in_time)
            attendance.save()
            return Response(
                {"message": "Out time updated successfully.", "data": {
                    "in_time": attendance.in_time,
                    "out_time": attendance.out_time,
                    "duration": attendance.duration
                }},
                status=status.HTTP_200_OK
            )
        else:
            # If no record exists, create a new attendance object with `in_time`
            if in_time_str.lower() == "in_time" or not in_time_str:
                in_time = now()  
            else:
                try:
                    in_time = make_aware(datetime.fromisoformat(in_time_str))
                except ValueError:
                    return Response(
                        {"error": "Invalid in_time format. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS)."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Create new attendance
            attendance = AttendanceModel.objects.create(
                attendance_user=user,
                in_time=in_time,
                out_time=out_time,
            )
            return Response(
                {"message": "In time saved successfully.", "data": {
                    "in_time": attendance.in_time,
                    "out_time": attendance.out_time,
                    "duration": attendance.duration
                }},
                status=status.HTTP_201_CREATED
            )





class InTimeAttendance(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            uuid = request.query_params.get("uuid")
            if uuid:
                try:
                    current_user = MyUser.objects.get(uuid=uuid)
                except MyUser.DoesNotExist:
                    return Response({"status": status.HTTP_404_NOT_FOUND, "message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            else:
                current_user = request.user
            
            latest_data = current_user.attendance_user.filter(in_time__date=datetime.now().date()).first()
            if not latest_data:
                return Response({"status": status.HTTP_404_NOT_FOUND, "message": "No attendance data found."}, status=status.HTTP_404_NOT_FOUND)
            
            if latest_data.in_time.date() == datetime.now().date():
                serialized_data = {
                    "id": latest_data.id,
                    "in_time": latest_data.in_time,
                    "out_time": latest_data.out_time,
                }
            else:
                serialized_data = {
                    "id": latest_data.id,
                }
                
            return Response({"status": status.HTTP_200_OK, "data": serialized_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GetAllAttendance(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            get_user = MyUser.objects.get(uuid=request.query_params.get("uuid"))
            if get_user.user_type == "Admin":
                attendance = AttendanceModel.objects.values("id", "attendance_user__first_name","attendance_user__last_name","attendance_user__designation", "in_time", "out_time", "duration",  "created_at").order_by("-id")
            else:
                attendance = get_user.attendance_user.values("id", "attendance_user__first_name","attendance_user__last_name", "attendance_user__designation","in_time", "out_time", "duration", "created_at").order_by("-id")
            paginator = StandardResultsSetPagination()
            paginated_queryset = paginator.paginate_queryset(attendance, request, view=self)
            return paginator.get_paginated_response(paginated_queryset)
        except Exception as e:
            return Response({"message": str(e), "code": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)



class AdminDashboardAttendance(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get total employee count excluding admins
        total_employee_count = MyUser.objects.exclude(user_type="Admin").count()

        # Get today's date
        today = datetime.now().date()

        # Calculate attendance for today
        count_attendance = AttendanceModel.objects.filter(in_time__date=today).count()

        # Calculate absent employees
        absent_count = total_employee_count - count_attendance

        # Calculate total Saturdays and Sundays in the current month
        year = today.year
        month = today.month
        total_days_in_month = monthrange(year, month)[1]
        first_day_of_month = datetime(year, month, 1).date()

        weekoff_count = sum(
            1
            for day in range(total_days_in_month)
            if (first_day_of_month + timedelta(days=day)).weekday() in [5, 6]
        )

        return Response({
            "status": status.HTTP_200_OK,
            "present": count_attendance,
            "total": total_employee_count,
            "absent": absent_count,
            "weekoff": weekoff_count,
        })


class RegularizationApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            current_user = MyUser.objects.filter(uuid=request.query_params.get("uuid")).first() or request.user
            if not current_user or not isinstance(current_user, MyUser):
                return Response({"message": "Invalid user.", "code": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
            existing_regularization = RegularizationModel.objects.filter(
                user_regularization=current_user,
                date=request.data['date']
            ).first()

            if existing_regularization:
                return Response({"message": "Regularization already applied for this date.", "code": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            RegularizationModel.objects.create(
                user_regularization=current_user,
                date=request.data['date'],
                in_time=request.data['in_time'],
                out_time=request.data['out_time'],
                reason=request.data['reason']
            )
            
            return Response({"code": status.HTTP_200_OK, "message": "Regularization applied successfully."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"message": str(e), "code": status.HTTP_404_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        
    
    def get(self, request):
        if request.user.user_type == "Admin":
            regularization = RegularizationModel.objects.values("id", "user_regularization__uuid", "user_regularization__first_name","user_regularization__last_name", "user_regularization__designation","in_time", "out_time", "reason", "approval", "date")
            paginator = StandardResultsSetPagination()
            paginated_queryset = paginator.paginate_queryset(regularization, request, view=self)
            return paginator.get_paginated_response(paginated_queryset)
        else:
            return Response({"status": status.HTTP_404_NOT_FOUND, "message": "Permission not allowed."}, status=status.HTTP_404_NOT_FOUND)
        

class ApprovalRegularise(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user_regularise = MyUser.objects.filter(uuid=request.data["uuid"]).first()
        regularise_obj = RegularizationModel.objects.filter(id=request.data["id"]).first()
        
        if user_regularise and regularise_obj:
            in_time_combined = datetime.combine(regularise_obj.date, regularise_obj.in_time)
            out_time_combined = datetime.combine(regularise_obj.date, regularise_obj.out_time)
            
            duration_seconds = (out_time_combined - in_time_combined).total_seconds()
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            seconds = int(duration_seconds % 60)
            
            duration = f"{hours}:{minutes:02}:{seconds:02}"
            
            AttendanceModel.objects.filter(attendance_user=user_regularise, in_time__date=regularise_obj.date).delete()
            if request.data["approval"]:
                AttendanceModel.objects.create(
                    attendance_user=user_regularise,
                    in_time=in_time_combined,
                    out_time=out_time_combined,
                    duration=duration
                )
            regularise_obj.approval = request.data["approval"]
            regularise_obj.save()
            return Response({"status": status.HTTP_200_OK})
        
        return Response({"status": status.HTTP_404_NOT_FOUND, "message": "Something went wrong."}, status=status.HTTP_404_NOT_FOUND)
    



class DashBoardMonthlyChart(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            year = int(request.query_params.get('year', datetime.now().year))
            month = int(request.query_params.get('month', datetime.now().month))

            start_date = datetime(year, month, 1).date()
            today = datetime.now().date()
            _, last_day = calendar.monthrange(year, month)
            end_date = min(datetime(year, month, last_day).date(), today)

            attendance_data = (
                AttendanceModel.objects.filter(
                    attendance_user__user_type='User',
                    in_time__date__range=(start_date, end_date)
                )
                .annotate(date=F('in_time__date'))  
                .values('date')
                .annotate(present_count=Count('id')) 
                .order_by('date')
            )

            daily_data = {date.strftime('%Y-%m-%d'): 0 for date in [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]}
            for data in attendance_data:
                daily_data[str(data['date'])] = data['present_count']

            labels = [datetime.strptime(date, '%Y-%m-%d').strftime('%d %b') for date in daily_data.keys()]
            data = list(daily_data.values())

            return Response({
                'year': year,
                'month': month,
                'labels': labels,
                'data': data
            }, status=200)

        except Exception as e:
            return Response({"error": "Unable to fetch monthly chart data.", "details": str(e)}, status=400)
        




from django.utils import timezone
class EmployeeAttendanceCalendar(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_uuid = request.GET.get('uuid')
        if user_uuid:
            user = MyUser.objects.filter(uuid=user_uuid).first()
        else:
            user = request.user

        if not user:
            return Response({"detail": "User not found"}, status=404)

        # Filter attendance data
        attendance_filter = AttendanceFilter(request.GET, queryset=AttendanceModel.objects.filter(attendance_user=user))
        attendance_data = attendance_filter.qs

        # Get year and month from request
        year = request.GET.get('year')
        month = request.GET.get('month')
        today = timezone.now().date()

        if not year or not month:
            # Default to a rolling 30-day window
            start_date = today - timedelta(days=30)
            end_date = today
        else:
            # Create start_date and end_date based on the requested year and month
            start_date = today.replace(year=int(year), month=int(month), day=1)
            if month == '12':
                end_date = today.replace(year=int(year), month=12, day=31)
            else:
                end_date = today.replace(year=int(year), month=int(month) + 1, day=1) - timedelta(days=1)

            # Ensure end_date does not extend beyond today
            end_date = min(end_date, today)

        # Generate date range and initialize calendar data
        date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
        calendar_data = []

        for date in date_range:
            # Weekends
            if date.weekday() in [5, 6]:  
                calendar_data.append({
                    'date': date,
                    'status': 'Week Off',
                })
                continue

            # Attendance entries
            attendance_entry = next((att for att in attendance_data if att.in_time.date() == date), None)
            if attendance_entry:
                calendar_data.append({
                    'date': date,
                    'status': 'Present',
                    'in_time': attendance_entry.in_time,
                    'out_time': attendance_entry.out_time,
                    'duration': attendance_entry.duration
                })
            else:
                calendar_data.append({'date': date, 'status': 'Absent'})

            # Leave entries
            leave_data = LeavesModel.objects.filter(leave_user=user, from_date__lte=date, to_date__gte=date)
            for leave_entry in leave_data:
                if leave_entry.status == 'Approved':
                    calendar_data.append({
                        'date': date,
                        'status': 'Leave',
                        'leave_type': leave_entry.leave_type,
                        'reason': leave_entry.reason
                    })

        # Sort data by date
        calendar_data.sort(key=lambda x: x['date'])
        return Response({"calendar_data": calendar_data})

    



class EmployeeDashboardCount(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_uuid = request.GET.get('uuid')
        if user_uuid:
            user = MyUser.objects.filter(uuid=user_uuid).first()
        else:
            user = request.user
        if not user:
            return Response({"detail": "User not found"}, status=404)
        today = timezone.now().date()
        start_date = user.joining_date if user.joining_date else today
        present_count = AttendanceModel.objects.filter(
            attendance_user=user,
            in_time__gte=start_date,
            in_time__lte=today
        ).values('in_time__date').distinct().count()
        absent_count = AttendanceModel.objects.filter(
            attendance_user=user,
            in_time__gte=start_date,
            in_time__lte=today
        ).filter(out_time__isnull=True).values('in_time__date').distinct().count()
        leave_data = LeavesModel.objects.filter(
            leave_user=user,
            status="Approved",
            from_date__gte=start_date,
            to_date__lte=today
        )
        total_used_leave = sum([leave.leave_duration() for leave in leave_data])
        leave_balance = LeaveBalanceModel.objects.filter(leave_balance_user=user).first()
        if leave_balance:
            earned_leave = leave_balance.earned_leave
            sick_leave = leave_balance.sick_leave
        else:
            earned_leave = sick_leave = 0

        total_leave_balance = earned_leave + sick_leave
        response_data = {
            "total_present": present_count,
            "total_absent": absent_count,
            "total_leave_balance": total_leave_balance,
            "total_used_leave": total_used_leave,
            "earned_leave":earned_leave,
            "sick_leave":sick_leave
            }

        return Response({"response_data":response_data})
    



class ApplyLeaveApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_uuid = request.data.get('uuid')
        if user_uuid:
            user = MyUser.objects.filter(uuid=user_uuid).first()
        else:
            user = request.user
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        leave_type = request.data.get('leave_type')
        from_date_str = request.data.get('from_date')
        to_date_str = request.data.get('to_date')
        reason = request.data.get('reason')
        try:
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"detail": "Invalid date format. Use 'YYYY-MM-DD'."}, status=status.HTTP_400_BAD_REQUEST)
        if not leave_type or not from_date or not to_date:
            return Response({"detail": "Leave type, from date, and to date are required."}, status=status.HTTP_400_BAD_REQUEST)
        if from_date < timezone.now().date() or to_date < timezone.now().date():
            return Response({"detail": "Leave dates cannot be in the past."}, status=status.HTTP_400_BAD_REQUEST)
        leave_balance = LeaveBalanceModel.objects.filter(leave_balance_user=user).first()
        if not leave_balance:
            return Response({"detail": "Leave balance not found for this user."}, status=status.HTTP_400_BAD_REQUEST)
        leave_duration = (to_date - from_date).days + 1
        if leave_type == 'Earned':
            if leave_balance.earned_leave < leave_duration:
                return Response({"detail": "Insufficient earned leave balance."}, status=status.HTTP_400_BAD_REQUEST)
        elif leave_type == 'Sick':
            if leave_balance.sick_leave < leave_duration:
                return Response({"detail": "Insufficient sick leave balance."}, status=status.HTTP_400_BAD_REQUEST)
        leave = LeavesModel(
            leave_user=user,
            leave_type=leave_type,
            from_date=from_date,
            to_date=to_date,
            reason=reason,
            status="Pending"
        )
        leave.save()

        return Response({
            "detail": "Leave applied successfully, awaiting approval.",
            "leave_id": leave.id,
            "leave_duration": leave_duration
        }, status=status.HTTP_201_CREATED)




class LeavesApi(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_uuid = request.query_params.get('uuid')
        user = MyUser.objects.filter(uuid=user_uuid).first() if user_uuid else request.user
        try:
            if user:
                leave = LeavesModel.objects.values(
                    "id", "leave_user__first_name", "leave_user__last_name", "leave_user__designation", "leave_type",
                    "from_date", "to_date", "reason", "status", "created_at")
            elif user:
                leave = user.leave_user.values(
                    "id", "leave_user__first_name", "leave_user__last_name", "leave_user__designation", "leave_type",
                    "from_date", "to_date", "reason", "status", "created_at")
            else:
                return Response({"message": "User not found", "code": 404}, status=status.HTTP_404_NOT_FOUND)

            paginator = StandardResultsSetPagination()
            paginated_queryset = paginator.paginate_queryset(leave, request, view=self)
            return paginator.get_paginated_response(paginated_queryset)

        except LeavesModel.DoesNotExist:
            return Response({"message": "No leaves found", "code": 404}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e), "code": status.HTTP_500_INTERNAL_SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ApprovedLeave(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            leave_id = request.data.get("leave_id")
            approval_status = request.data.get("status")  
            if not leave_id or not approval_status:
                return Response(
                    {"message": "Leave ID and status are required.", "code": 400},
                    status=status.HTTP_400_BAD_REQUEST,)
            leave = LeavesModel.objects.filter(id=leave_id).first()
            if not leave:
                return Response(
                    {"message": "Leave record not found.", "code": 404},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if request.user.user_type != "Admin":
                return Response(
                    {"message": "You are not authorized to approve leaves.", "code": 403},
                    status=status.HTTP_403_FORBIDDEN,
                )
            leave.status = approval_status
            leave.approved_by = request.user
            leave.approved_on = timezone.now()
            leave.save()
            return Response(
                {"message": f"Leave has been {approval_status.lower()} successfully.", "code": 200},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": str(e), "code": status.HTTP_500_INTERNAL_SERVER_ERROR},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



class AttendanceManagementApi(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.now().date()
        year, month = today.year, today.month
        total_days_in_month = monthrange(year, month)[1]
        first_day_of_month = datetime(year, month, 1).date()
        weekdays = [
            (first_day_of_month + timedelta(days=i)).weekday()
            for i in range(total_days_in_month)
        ]
        total_weekoffs = weekdays.count(5) + weekdays.count(6)

        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        search_name = request.query_params.get('name', '').strip()
        uuid = request.query_params.get('uuid')
        if uuid:
            users = MyUser.objects.filter(uuid=uuid).exclude(user_type="Admin")
        else:
            users = MyUser.objects.exclude(user_type="Admin")
        if search_name:
            users = users.filter(
                Q(first_name__icontains=search_name) | Q(last_name__icontains=search_name) | Q(designation__icontains=search_name)
            )
        response_data = []
        for user in users:
            attendance_queryset = AttendanceModel.objects.filter(attendance_user=user)
            leaves_queryset = LeavesModel.objects.filter(leave_user=user, status="Approved")

            if from_date:
                from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
                attendance_queryset = attendance_queryset.filter(in_time__date__gte=from_date_obj)
                leaves_queryset = leaves_queryset.filter(from_date__gte=from_date_obj)

            if to_date:
                to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
                attendance_queryset = attendance_queryset.filter(in_time__date__lte=to_date_obj)
                leaves_queryset = leaves_queryset.filter(to_date__lte=to_date_obj)

            days_worked = attendance_queryset.count()

            el_applied = sum(
                leave.leave_duration()
                for leave in leaves_queryset if leave.leave_type == "Earned"
            )
            sl_applied = sum(
                leave.leave_duration()
                for leave in leaves_queryset if leave.leave_type == "Sick"
            )

            leave_balance = LeaveBalanceModel.objects.filter(leave_balance_user=user).first()
            el_available = leave_balance.earned_leave if leave_balance else 0
            sl_available = leave_balance.sick_leave if leave_balance else 0
            lop = total_days_in_month - total_weekoffs - days_worked - (el_applied + sl_applied)

            response_data.append({
                "Employee_Name": f"{user.first_name} {user.last_name}",
                "Designation": user.designation,
                "Days_Worked": days_worked,
                "lop": max(lop, 0),
                "Week_Off": total_weekoffs,
                "EL_Applied": el_applied,
                "SL_Applied": sl_applied,
                "EL_SL_Available": f"EL: {el_available}, SL: {sl_available}",
            })

        paginator = StandardResultsSetPagination()
        paginated_data = paginator.paginate_queryset(response_data, request)

        return paginator.get_paginated_response(paginated_data)


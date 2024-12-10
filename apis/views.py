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
from datetime import datetime
from django.db.models import Q



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
            
            latest_data = current_user.attendance_user.first()
            if not latest_data:
                return Response({"status": status.HTTP_404_NOT_FOUND, "message": "No attendance data found."}, status=status.HTTP_404_NOT_FOUND)
            
            serialized_data = {
                "id": latest_data.id,
                "in_time": latest_data.in_time,
                "out_time": latest_data.out_time,
            }
            
            return Response({"status": status.HTTP_200_OK, "data": serialized_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
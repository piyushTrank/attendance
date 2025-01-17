from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apis.models import *




class EmployeeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)

    class Meta:
        model = MyUser
        fields = [
            'first_name', 'last_name', 'emp_code','email', 'phone_number',
            'gender', 'dob', 'joining_date', 'designation', 'address', 'password'
        ]

    def validate_email(self, value):
        """Validate if email is unique."""
        if MyUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    def validate_emp_code(self, value):
        if MyUser.objects.filter(emp_code=value).exists():
            raise serializers.ValidationError("A user with this employee code already exists.")
        return value

    def create(self, validated_data):
        """Create a new user with validated data."""
        email = validated_data.pop('email').lower()
        password = validated_data.pop('password')
        
        user = MyUser.objects.create(
            email=email,
            user_type="User",
            is_active=True,
            **validated_data
        )
        user.set_password(password)
        user.save()
        return user
    

class EmployeeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = [
            'first_name', 'last_name', 'phone_number',
            'gender', 'dob', 'joining_date', 'designation', 'address']

    def to_internal_value(self, data):
        """Remove keys with empty values before validation."""
        cleaned_data = {key: value for key, value in data.items() if value not in ["", None]}
        return super().to_internal_value(cleaned_data)

    def update(self, instance, validated_data):
        """Update only provided fields."""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class UserDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocument
        fields = ['id','document_type', 'file', 'uploaded_at']






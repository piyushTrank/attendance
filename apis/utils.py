from datetime import datetime

def user_directory_path(instance, filename):
        """Generate file path for new image upload."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_type = "InTime" if instance.image_type == 'IN' else "OutTime"
        return f'attendance/{instance.image_user.attendance_user.first_name}/{image_type}/{timestamp}_{filename}'
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):

        if not email:
            raise ValueError ("Email is required")
        
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,password=None,**extra_fields):

        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_active",True)
        extra_fields.setdefault("is_superuser",True)

        if not extra_fields.get("is_staff"):
            raise ValueError ("is_staff must be true for superuser")
        
        if not extra_fields.get("is_superuser"):
            raise ValueError ("is_superuser must be true for superuser")
        
        if not extra_fields.get("is_active"):
            raise ValueError ("is_active must be true for superuser")
        
        return self.create_user(email,password,**extra_fields)
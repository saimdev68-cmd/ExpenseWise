from django.contrib.auth import authenticate

from .service_result import ServiceResult


class LoginService:
    """
    Login Service
    """
    @staticmethod
    def check_user(data,request):
        email = data.get("email")
        password = data.get("password")
        user = authenticate(request,email=email,password=password)
        if user is None:
            return ServiceResult(success=False,message="Invalid Email or Password")
        return ServiceResult(success=True,message="Login Successfully",user=user)
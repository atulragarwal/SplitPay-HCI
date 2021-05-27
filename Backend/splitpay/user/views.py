from rest_auth.registration.views import RegisterView

class CustomRegisterView(RegisterView):
    queryset = User.objects.all()
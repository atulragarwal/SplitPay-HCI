from rest_auth.registration.serializers import RegisterSerializer

class CustomRegisterSerializer(RegisterSerializer):

    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)
    balance = serializers.IntegerField(required=True)

    def get_cleaned_data(self):
        super(CustomRegisterSerializer, self).get_cleaned_data()

        return {
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'name': self.validated_data.get('name', ''),
            'phone_number': self.validated_data.get('phone_number', ''),
            'balance': self.validated_data.get('balance', ''),
            'profile_pic': self.validated_data.get('profile_pic', ''),
        }

class CustomUserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email','name','phone_number','balance','profile_pic')
        read_only_fields = ('email',)
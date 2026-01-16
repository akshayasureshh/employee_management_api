from rest_framework import serializers
from .models import User, Employee
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=_('Email'),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    access = serializers.CharField(
        label=_('Access Token'),
        read_only=True
    )
    refresh = serializers.CharField(
        label=_('Refresh Token'),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )
            if not user:
                msg = _('Invalid credentials')
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.is_active:
                msg = _('User account is disabled')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Email and password are required')
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_full_name', read_only=True)
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'name',
            'password',
            'is_staff',
            'is_active',
            'created_at'
        ]
        read_only_fields = [
            'id',
            'is_staff',
            'is_active',
            'created_at'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'password': {
                'max_length': 64,
                'min_length': 8,
                'write_only': True,
                'trim_whitespace': False,
                'required': True
            }
        }
        
    def get_full_name(self, obj):
        return obj.name
        
class EmployeeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model =Employee
        fields = ['id', 'department', 'role', 'date_joined','name', 'email']
        read_only_fields = ['id', 'date_joined']
        
        
    def create(self, validated_data):
        user = self.context['request'].user
        if hasattr(user, 'employee'):
            raise serializers.ValidationError(
                "You already have an employee record.Can't create another."
            )
        employee = Employee.objects.create(user=user, **validated_data)
        return employee

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
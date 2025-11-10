from rest_framework import serializers
from .models import Role, Permission, RolePermission, User


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['role_id', 'name', 'description']
        read_only_fields = ['role_id']


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['permission_id', 'name', 'description']
        read_only_fields = ['permission_id']


class RolePermissionSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)

    class Meta:
        model = RolePermission
        fields = ['id', 'role', 'role_name', 'permission', 'permission_name']


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'password',
            'role', 'role_name', 'is_active', 'is_staff', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'required': False}  # Make role optional
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        
        # Set default role to 'Reader' if not provided
        if 'role' not in validated_data:
            try:
                reader_role = Role.objects.get(name='Reader')
                validated_data['role'] = reader_role
            except Role.DoesNotExist:
                raise serializers.ValidationError({'role': 'Reader role not found. Please create it first.'})
        
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

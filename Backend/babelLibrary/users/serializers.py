from rest_framework import serializers
from .models import Role, Permission, RolePermission, User, Bookmark, ReadingHistory


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


class BookmarkSerializer(serializers.ModelSerializer):
    """Serializer for user bookmarks."""
    series_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['bookmark_id', 'user', 'series', 'series_details', 'created_at']
        read_only_fields = ['bookmark_id', 'user', 'created_at']

    def get_series_details(self, obj):
        """Return basic series information."""
        from library.serializers import SeriesSerializer
        return SeriesSerializer(obj.series).data

    def create(self, validated_data):
        # Set the user from the request context
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class ReadingHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for reading history.
    
    Note: The create method uses update_or_create to automatically update
    existing reading history records for the same user/series combination.
    This ensures only one reading history entry exists per user per series,
    with the most recent chapter they read.
    """
    series_title = serializers.CharField(source='series.title', read_only=True)
    chapter_number = serializers.IntegerField(source='chapter.chapter_number', read_only=True)
    chapter_title = serializers.CharField(source='chapter.title', read_only=True)

    class Meta:
        model = ReadingHistory
        fields = [
            'history_id', 'user', 'series', 'chapter', 
            'series_title', 'chapter_number', 'chapter_title',
            'last_read_at', 'created_at'
        ]
        read_only_fields = ['history_id', 'user', 'last_read_at', 'created_at']

    def create(self, validated_data):
        """
        Create or update reading history for a user/series combination.
        
        This method intentionally uses update_or_create instead of create
        to ensure only one reading history entry exists per user per series.
        If a record already exists, it will be updated with the new chapter.
        """
        # Set the user from the request context
        user = self.context['request'].user
        validated_data['user'] = user
        
        # Update or create reading history for this user/series combination
        obj, created = ReadingHistory.objects.update_or_create(
            user=user,
            series=validated_data['series'],
            defaults={'chapter': validated_data['chapter']}
        )
        return obj
    
    def update(self, instance, validated_data):
        """Update the chapter for an existing reading history record."""
        instance.chapter = validated_data.get('chapter', instance.chapter)
        instance.save()
        return instance

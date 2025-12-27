from django.contrib.auth.models import User
from .models import *
from django .contrib.auth.password_validation import validate_password
from rest_framework import serializers



class UserProfileSerializer(serializers.ModelSerializer):
  profile_picture = serializers.SerializerMethodField()
  
  def get_profile_picture(self, obj):
    if obj.profile_picture:
      return obj.profile_picture.url
    return None
  
  class Meta:
    model = UserProfile
    fields = ['bio', 'profile_picture']


class UserSerializer(serializers.ModelSerializer):
  profile = UserProfileSerializer(read_only=True)
  
  class Meta:
    model = User
    fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']


class UserUpdateSerializer(serializers.ModelSerializer):
  bio = serializers.CharField(source='profile.bio', allow_blank=True, required=False)
  profile_picture = serializers.ImageField(source='profile.profile_picture', required=False, allow_null=True)
  
  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'email', 'bio', 'profile_picture']
  
  def update(self, instance, validated_data):
    # Update User fields
    instance.first_name = validated_data.get('first_name', instance.first_name)
    instance.last_name = validated_data.get('last_name', instance.last_name)
    instance.email = validated_data.get('email', instance.email)
    instance.save()
    
    # Update Profile fields
    profile_data = validated_data.get('profile', {})
    if profile_data:
      profile = instance.profile
      profile.bio = profile_data.get('bio', profile.bio)
      if 'profile_picture' in profile_data:
        profile.profile_picture = profile_data.get('profile_picture')
      profile.save()
    
    return instance



class RegisterSerializer(serializers.ModelSerializer):
  password = serializers.CharField(write_only = True)
  class Meta:
    model  = User
    fields = ['email', 'username','password']
  def create(self, validated_data):
    user = User(
      username = validated_data['username'],
      email = validated_data['email'].lower()
    )
    user.set_password(validated_data['password'])
    user.save()
    return user
  def validate_password(self, value):
    validate_password(value)
    return value
  def validate_email(self, value):
    value = value.lower()
    if User.objects.filter(email = value).exists():
      raise serializers.ValidationError("Email already taken.")
    return value
  def validate_username(self, value):
    if User.objects.filter(username = value).exists():
      raise serializers.ValidationError("Username already taken.")
    return value



class CategorySerializer(serializers.ModelSerializer):
  post_count = serializers.SerializerMethodField()
  def get_post_count(self,category):
    return category.posts.count()
  class Meta:
    model = Category
    fields= ['id', 'title', 'image', 'slug', 'post_count']




#Serializer to List Post and Detail Post
class PostSerializer(serializers.ModelSerializer):
  user = serializers.StringRelatedField()
  category = CategorySerializer()
  class Meta:
    model = Post
    fields = '__all__'



#Serializer to Create Post
class PostCreateSerializer(serializers.ModelSerializer):
  class Meta:
    model = Post
    fields = ['title', 'image', 'description', 'category']



class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    post = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'comment', 'created_at']


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment']


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("No user found with this email address.")
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data 
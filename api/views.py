
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from api import serializer as api_serializer
from api import models as api_models
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
#Custom permission
class IsOwnerOrReadOnly(permissions.BasePermission):
 def has_object_permission(self, request, view, obj):
  if request.method in permissions.SAFE_METHODS:
    return True
  return obj.user == request.user
 
#Custom Pagination for Posts
class PostPagination(PageNumberPagination):
  page_size = 10
  page_query_param= 'page'


#Authentication Views
class ProfileView(APIView):
  permission_classes = [permissions.IsAuthenticated]
  
  def get(self, request):
    serializer = api_serializer.UserSerializer(request.user)
    return Response(serializer.data)
  
  def put(self, request):
    serializer = api_serializer.UserUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response(api_serializer.UserSerializer(request.user).data)
    return Response(serializer.errors, status=400)
  
  def patch(self, request):
    serializer = api_serializer.UserUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response(api_serializer.UserSerializer(request.user).data)
    return Response(serializer.errors, status=400)
  

class RegisterView(generics.CreateAPIView):
  serializer_class = api_serializer.RegisterSerializer
  permission_classes = [permissions.AllowAny]

#Blog Post Views
class CategoryView(generics.ListAPIView):
  permission_classes= [permissions.AllowAny]
  queryset = api_models.Category.objects.all()
  serializer_class = api_serializer.CategorySerializer

#List Posts
class PostListView(generics.ListAPIView):
  queryset = api_models.Post.objects.all().order_by('-created_at')
  serializer_class = api_serializer.PostSerializer
  permission_classes = [permissions.IsAuthenticated]
  pagination_class = PostPagination

# Post Detail
class PostDetailView(generics.RetrieveAPIView):
  queryset = api_models.Post.objects.select_related('user', 'category').all()
  serializer_class = api_serializer.PostSerializer
  permission_classes = [permissions.IsAuthenticated]
  lookup_field = 'slug'
  
  def retrieve(self, request, *args, **kwargs):
    instance = self.get_object()
    instance.views += 1
    instance.save()
    serializer = self.get_serializer(instance)
    return Response(serializer.data)

# Create a Post
class PostCreateView(generics.CreateAPIView):
  serializer_class = api_serializer.PostCreateSerializer
  permission_classes = [permissions.IsAuthenticated]
  def perform_create(self, serializer):
    serializer.save(user = self.request.user)

#Update a Post
class PostUpdateView(generics.UpdateAPIView):
  queryset  = api_models.Post.objects.all()
  permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
  serializer_class = api_serializer.PostCreateSerializer
  lookup_field = 'slug'

#Delete a post
class PostDeleteView(generics.DestroyAPIView):
  queryset = api_models.Post.objects.all()
  permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
  lookup_field = 'slug'

#gets comments for a specific post
class CommentListView(generics.ListAPIView):
    serializer_class = api_serializer.CommentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        slug = self.kwargs['slug']
        return api_models.Comment.objects.filter(post__slug=slug).order_by('-created_at')


#post a comment
class CommentCreateView(generics.CreateAPIView):
    serializer_class = api_serializer.CommentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        slug = self.kwargs['slug']
        post = api_models.Post.objects.get(slug=slug)
        serializer.save(user=self.request.user, post=post)


# Password Reset Views
class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = api_serializer.PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Invalidate any existing unused tokens for this user
            api_models.PasswordResetToken.objects.filter(user=user, used=False).update(used=True)
            
            # Create new token
            reset_token = api_models.PasswordResetToken.objects.create(user=user)
            
            # Create reset link
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token.token}"
            
            # Send email
            subject = 'Password Reset Request - Self Blog'
            message = f"""Hello {user.username},

You requested to reset your password for Self Blog.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
Self Blog Team
"""
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                print(f"✅ Password reset email sent successfully to {email}")
                print(f"🔗 Reset URL: {reset_url}")
                return Response({
                    'message': 'Password reset link has been sent to your email.',
                    'reset_url': reset_url  # For testing - remove in production
                }, status=200)
            except Exception as e:
                # Log the error for debugging
                print(f"❌ Email sending failed: {str(e)}")
                import traceback
                traceback.print_exc()
                # Return the reset URL for testing when email fails
                return Response({
                    'message': 'Email service is currently unavailable. Please use the link below.',
                    'reset_url': reset_url
                }, status=200)
        
        return Response(serializer.errors, status=400)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = api_serializer.PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            
            try:
                reset_token = api_models.PasswordResetToken.objects.get(token=token)
                
                if not reset_token.is_valid():
                    return Response({'error': 'This reset link has expired or already been used.'}, status=400)
                
                # Validate password
                try:
                    validate_password(password, user=reset_token.user)
                except ValidationError as e:
                    return Response({'password': list(e.messages)}, status=400)
                
                # Reset password
                user = reset_token.user
                user.set_password(password)
                user.save()
                
                # Mark token as used
                reset_token.used = True
                reset_token.save()
                
                return Response({'message': 'Password has been reset successfully.'}, status=200)
                
            except api_models.PasswordResetToken.DoesNotExist:
                return Response({'error': 'Invalid reset token.'}, status=400)
        
        return Response(serializer.errors, status=400)
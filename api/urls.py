from django.urls import path
from api import views as api_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns=[
  path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
  path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
  path('profile/', api_views.ProfileView.as_view()), 
  path('register/', api_views.RegisterView.as_view()),
  path('categories/', api_views.CategoryView.as_view()),
  path('post-list/', api_views.PostListView.as_view()),
  path('post-detail/<slug:slug>/', api_views.PostDetailView.as_view()),
  path('post-create/', api_views.PostCreateView.as_view()), 
  path('post-update/<slug:slug>/', api_views.PostUpdateView.as_view()), 
  path('post-delete/<slug:slug>/', api_views.PostDeleteView.as_view()),
  path('create-comment/<slug:slug>/', api_views.CommentCreateView.as_view()),
  path('comment-list/<slug:slug>/', api_views.CommentListView.as_view()),
  path('password-reset-request/', api_views.PasswordResetRequestView.as_view()),
  path('password-reset-confirm/', api_views.PasswordResetConfirmView.as_view()), 
]
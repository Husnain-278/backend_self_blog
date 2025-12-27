from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
import shortuuid
from cloudinary.models import CloudinaryField
import uuid
from django.utils import timezone
from datetime import timedelta
# Create your models here.


class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
  bio = models.TextField(blank=True, null=True)
  profile_picture = CloudinaryField('image', folder='profile_pictures', blank=True, null=True)
  
  def __str__(self):
    return f"{self.user.username}'s Profile"
  
  class Meta:
    verbose_name = "User Profile"
    verbose_name_plural = "User Profiles"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
  instance.profile.save()


class Category(models.Model):
  title = models.CharField(max_length=100)
  image = CloudinaryField('image',folder='category_images',blank=True,null=True)
  slug = models.SlugField(unique = True, blank = True)
  def __str__(self):
    return self.title
  class Meta:
    verbose_name_plural = "Categories"
  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.title)
    return super().save(*args, **kwargs)



class Post(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  category = models.ForeignKey(Category, on_delete= models.CASCADE, related_name='posts')
  title = models.CharField(max_length=200)
  image = CloudinaryField('image',folder = 'post_images',blank=True,null=True)
  description = models.TextField( blank=True)
  slug = models.SlugField(unique = True, blank=True)
  views = models.IntegerField(default=0)
  created_at = models.DateTimeField(auto_now_add=True)
  def __str__(self):
    return self.title
  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.title) + "-" + shortuuid.uuid()[:2]
    return super().save(*args, **kwargs)
  
class Comment(models.Model):
  post = models.ForeignKey(Post, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  comment = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.post.title} comment by {self.user.username}"


class PasswordResetToken(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
  created_at = models.DateTimeField(auto_now_add=True)
  expires_at = models.DateTimeField()
  used = models.BooleanField(default=False)

  def save(self, *args, **kwargs):
    if not self.expires_at:
      self.expires_at = timezone.now() + timedelta(hours=1)
    super().save(*args, **kwargs)

  def is_valid(self):
    return not self.used and timezone.now() < self.expires_at

  def __str__(self):
    return f"Password reset token for {self.user.username}"

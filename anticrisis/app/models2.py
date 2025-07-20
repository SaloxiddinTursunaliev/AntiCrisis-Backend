from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
import uuid
from datetime import datetime
import os

def avatar_upload_to(instance, filename):
    username = instance.user.username.replace(" ", "_")  # Optional: replace spaces with underscores
    ext = os.path.splitext(filename)[1] or '.jpg'
    return f"avatars/{username}_avatar{ext}"

def banner_upload_to(instance, filename):
    username = instance.user.username.replace(" ", "_")  # Optional
    ext = os.path.splitext(filename)[1] or '.jpg'
    return f"banners/{username}_banner{ext}"

class BusinessProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business_profile')
    business_name = models.CharField(max_length=255)
    avatar_picture = models.ImageField(upload_to=avatar_upload_to, null=True, blank=True)
    banner_picture = models.ImageField(upload_to=banner_upload_to, null=True, blank=True)
    followers_count = models.PositiveIntegerField(default=0)
    followings_count = models.PositiveIntegerField(default=0)
    about = models.TextField(null=True, blank=True, default='')
    contact_phone = models.CharField(max_length=15, null=True, blank=True, default='')
    contact_email = models.EmailField(null=True, blank=True, default='')
    website = models.URLField(null=True, blank=True, default='')
    address = models.TextField(null=True, blank=True, default='')
    location_coordinates = models.CharField(max_length=100, null=True, blank=True, default='')
    linked_profiles = models.ManyToManyField('self', symmetrical=False, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['business_name']),
        ]

    def __str__(self):
        return self.business_name
    
@receiver(pre_save, sender=BusinessProfile)
def delete_old_files(sender, instance, **kwargs):
    if not instance.pk:
        return

    old = sender.objects.get(pk=instance.pk)

    if old.avatar_picture and old.avatar_picture != instance.avatar_picture:
        old.avatar_picture.delete(save=False)

    if old.banner_picture and old.banner_picture != instance.banner_picture:
        old.banner_picture.delete(save=False)

class BusinessType(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    is_parent = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

class ClosureTable(models.Model):
    ancestor = models.ForeignKey(BusinessType, related_name='ancestor_set', on_delete=models.CASCADE)
    descendant = models.ForeignKey(BusinessType, related_name='descendant_set', on_delete=models.CASCADE)
    depth = models.PositiveIntegerField()  # Depth from ancestor to descendant

    class Meta:
        unique_together = ('ancestor', 'descendant')
        indexes = [
            models.Index(fields=['ancestor', 'descendant']),
        ]

class BusinessProfileType(models.Model):
    profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE)
    business_type = models.ForeignKey(BusinessType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('profile', 'business_type')
        indexes = [
            models.Index(fields=['profile', 'business_type']),
        ]
        
class Discount(models.Model):
    issuer = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='issued_discounts')
    recipient = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='received_discounts')
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    redeem_limit = models.DecimalField(max_digits=10, decimal_places=2)
    redeem_used = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['issuer', 'recipient']),
            models.Index(fields=['created_at']),
        ]

class Follow(models.Model):
    follower = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', 'following']),
            models.Index(fields=['created_at']),
        ]

class Notification(models.Model):
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['business_profile', 'is_read']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'Notification for {self.business_profile.business_name}'



def post_image_upload_to(instance, filename):
    # Generate a unique identifier using UUID and current timestamp
    unique_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}"
    ext = os.path.splitext(filename)[1] or '.jpg'  # Get the file extension
    
    return f"posts/{unique_id}{ext}"

class Post(models.Model):
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='posts')
    description = models.TextField()
    post_image = models.ImageField(upload_to=post_image_upload_to, null=True, blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['likes_count']),
        ]

    def __str__(self):
        return f'Post by {self.business_profile.business_name}'
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
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

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    business_name = models.CharField(max_length=255)
    avatar_url = models.ImageField(upload_to=avatar_upload_to, null=True, blank=True)
    banner_url = models.ImageField(upload_to=banner_upload_to, null=True, blank=True)
    
    # Denormalized counts
    followers_count = models.PositiveIntegerField(default=0)
    followings_count = models.PositiveIntegerField(default=0)
    discounts_received_count = models.PositiveIntegerField(default=0)
    discounts_used_count = models.PositiveIntegerField(default=0)

    # Contact & meta info
    about = models.TextField(null=True, blank=True, default='')
    phone = models.CharField(max_length=15, null=True, blank=True, default='')
    email = models.EmailField(null=True, blank=True, default='')
    website = models.URLField(null=True, blank=True, default='')
    address = models.TextField(null=True, blank=True, default='')
    location_coordinates = models.CharField(max_length=100, null=True, blank=True, default='')

    # Business network
    linked_profiles = models.ManyToManyField('self', symmetrical=False, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['business_name']),
        ]

    def __str__(self):
        return self.business_name

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

class UserBusinessType(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business_type = models.ForeignKey(BusinessType, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'business_type')
        indexes = [
            models.Index(fields=['user', 'business_type']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.business_type.name}"
    
class Discount(models.Model):
    issuer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_discounts')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_discounts')
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    redeem_limit = models.DecimalField(max_digits=10, decimal_places=2)
    redeem_used = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['issuer', 'recipient']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'Discount {self.percentage}% from {self.issuer.username} to {self.recipient.username}'

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', 'following']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        SYSTEM = 'system', 'System'
        POST = 'post', 'Post'
        FOLLOW = 'follow', 'Follow'
        BUSINESS = 'business', 'Business'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        db_index=True
    )

    message = models.TextField()
    type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        db_index=True
    )

    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Optional generic relation to source object (Post, Follow, etc.)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True
    )
    object_id = models.PositiveBigIntegerField(null=True, blank=True, db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['type']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification to {self.user.username}: {self.message[:40]}'



def post_image_upload_to(instance, filename):
    # Generate a unique identifier using UUID and current timestamp
    unique_id = f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex}"
    ext = os.path.splitext(filename)[1] or '.jpg'  # Get the file extension
    
    return f"posts/{unique_id}{ext}"

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')

    description = models.TextField(null=True, blank=True, default='')
    post_image = models.ImageField(upload_to=post_image_upload_to, null=True, blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['likes_count']),
            models.Index(fields=['user']),  # Optional: speeds up filtering by user
        ]

    def __str__(self):
        return f'Post by {self.user.username}'
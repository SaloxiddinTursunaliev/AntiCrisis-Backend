from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.core.files.storage import default_storage

from .models2 import Profile, Follow, Discount

# Clean up old avatar/banner images when updated
@receiver(pre_save, sender=Profile)
def delete_old_files(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    if old_instance.avatar_url and old_instance.avatar_url != instance.avatar_url:
        if default_storage.exists(old_instance.avatar_url.name):
            old_instance.avatar_url.delete(save=False)

    if old_instance.banner_url and old_instance.banner_url != instance.banner_url:
        if default_storage.exists(old_instance.banner_url.name):
            old_instance.banner_url.delete(save=False)

@receiver(pre_save, sender=Profile)
def delete_old_filesOld(sender, instance, **kwargs):
    if not instance.pk:
        return

    old = sender.objects.get(pk=instance.pk)

    if old.avatar_url and old.avatar_url != instance.avatar_url:
        old.avatar_url.delete(save=False)

    if old.banner_url and old.banner_url != instance.banner_url:
        old.banner_url.delete(save=False)

# # Update followers and followings counts
# @receiver([post_save, post_delete], sender=Follow)
# def update_follow_counts(sender, instance, **kwargs):
#     follower = instance.follower
#     following = instance.following

#     follower.followings_count = Follow.objects.filter(follower=follower).count()
#     following.followers_count = Follow.objects.filter(following=following).count()

#     follower.save(update_fields=['followings_count'])
#     following.save(update_fields=['followers_count'])

@receiver([post_save, post_delete], sender=Discount)
def update_discount_counts(sender, instance, **kwargs):
    try:
        recipient_profile = instance.recipient.profile
        issuer_profile = instance.issuer.profile
    except Profile.DoesNotExist:
        return

    issuer_profile.discounts_used_count = Discount.objects.filter(issuer=instance.issuer, redeem_used__gt=0).count()
    recipient_profile.discounts_received_count = Discount.objects.filter(recipient=instance.recipient).count()

    issuer_profile.save(update_fields=['discounts_used_count'])
    recipient_profile.save(update_fields=['discounts_received_count'])
    
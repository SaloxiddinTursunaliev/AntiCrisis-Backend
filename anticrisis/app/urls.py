from django.urls import path
from .auth.sign_up import signup
from .auth.sign_in import signin
from .auth.sign_out import signout
from .feeds.feeds import get_feeds
from .discount.discount import discounts, discount_add
from .search.search import search_businesses
from .search.search_by_id import get_business_by_id
from .profile.profile import get_profile
from .profile.profile_settings.profile_edit import profile_edit
from .profile.profile_settings.business_details_edit import business_details_edit
from .profile.get_posts import profile_posts
from.profile.post import post
from .profile.follow import follow_user

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('signin/', signin, name='signin'),
    path('signout/', signout, name='signout'),
    path('feeds/', get_feeds, name='get_feeds'),
    path('discounts/', discounts, name='discounts'),
    path('discount/', discount_add, name='discount_add'),
    path('search/', search_businesses, name='search_businesses'),
    path('business/<int:business_id>/', get_business_by_id, name='get_business_by_id'),

    path('profile/edit/', profile_edit, name='profile_edit'),
    path('profile/edit/business_details/', business_details_edit, name='business_details_edit'),
    
    path('profile/<str:username>/follow/', follow_user, name='follow_user'),

    path('profile/post/', post, name='post'),
    path('profile/<str:username>/posts/', profile_posts, name='profile_posts'),

    path('profile/<str:username>/', get_profile, name='get-profile'),
]
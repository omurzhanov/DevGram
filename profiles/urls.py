from django.urls import path
from .views import (
    my_profile_view,
    invites_received_view,
    ProfileListView,
    send_invitation, remove_from_friends,
    reject_invitation, accept_invitation,
    ProfileDetailView, FriendsListView
)

app_name = 'profiles'

urlpatterns = [
    path('', ProfileListView.as_view(), name='all-profiles-view'),
    path('my-friends/', FriendsListView.as_view(), name='my-friends-view'),
    path('myprofile/', my_profile_view, name='my-profile-view'),
    path('my-invites/', invites_received_view, name='my-invites-view'),
    path('send-invite/', send_invitation, name='send-invite'),
    path('remove-friend/', remove_from_friends, name='remove-friend'),
    path('<slug>/', ProfileDetailView.as_view(), name='profile-detail-view'),
    path('my-invites/accept/', accept_invitation, name='accept-invite'),
    path('my-invites/reject/', reject_invitation, name='reject-invite'),
]
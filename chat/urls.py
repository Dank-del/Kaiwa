from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("share/", views.share, name="share"),
    path("chat/", views.chat, name="chat"),
    # path("<str:room_name>/", views.room, name="room"),
    path("start_dm/<int:user_id>/", views.start_direct_message, name="start_dm"),
    path(
        "exchange_message/<int:dm_id>/", views.exchange_message, name="exchange_message"
    ),
    path("room/dms/", views.user_dms, name="direct_messages"),
    path("list/", views.user_rooms, name="chats"),
    path("room/<str:room_name>/", views.room, name="room"),
    path("room/manage/<int:room_id>/", views.manage_room, name="manage_room"),
]

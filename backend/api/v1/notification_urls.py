from django.urls import path
from api.v1.views.notification_views import NotificationListView, NotificationReadView, NotificationReadAllView

urlpatterns = [
    path("notifications/", NotificationListView.as_view(), name="notifications-list"),
    path("notifications/<uuid:pk>/read/", NotificationReadView.as_view(), name="notifications-read"),
    path("notifications/read-all/", NotificationReadAllView.as_view(), name="notifications-read-all"),
]

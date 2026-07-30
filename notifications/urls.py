from django.urls import path

from . import views


urlpatterns = [
    path("",views.NotificationListView.as_view(),name="list"),
    path("<int:pk>/read/",views.MarkNotificationReadView.as_view(),name="read"),
    path("read-all/",views.MarkAllNotificationsReadView.as_view(),name="read_all"),
    path("<int:pk>/delete/",views.NotificationDeleteView.as_view(),name="delete"),
]
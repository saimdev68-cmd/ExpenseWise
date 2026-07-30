from .models import Notification


def notification_context(request):
    context = {"unread_notification_count": 0,"latest_notifications": []}
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user)
        context["unread_notification_count"] = notifications.filter(is_read=False).count()
        context["latest_notifications"] = notifications.filter(is_read=False)[:5]
    return context
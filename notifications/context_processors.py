from .models import Notification


def notification_context(request):
    context = {"unread_notification_count": 0}
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user)
        context["unread_notification_count"] = notifications.filter(is_read=False).count()
    return context
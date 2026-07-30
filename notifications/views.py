from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, View
from django.shortcuts import redirect
from django.http import JsonResponse
from django.template.loader import render_to_string

from .models import Notification

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notification_list.html"
    context_object_name = "notifications"
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            html = render_to_string(
                "partials/notification_list.html",
                context,
                request=self.request,
            )
            return JsonResponse({"html": html})
        return super().render_to_response(context, **response_kwargs)

class NotificationDeleteView(LoginRequiredMixin, DeleteView):
    model = Notification
    success_url = reverse_lazy("list")

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # Get filtered queryset
            queryset = self.get_queryset()
            
            return JsonResponse({
                "success": True,
                "has_notifications": queryset.exists(),
                "count": queryset.count(),
            })
        
        messages.success(request, "Notification deleted successfully.")
        return redirect(self.success_url)

class MarkNotificationReadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        notification = Notification.objects.filter(user=request.user, pk=pk).first()
        if notification:
            notification.mark_as_read()
            if notification.url:
                return redirect(notification.url)
            return redirect("list")
        messages.error(request, "Notification not found.")
        return redirect("list")

class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    def get(self, request):
        # Get count of unread notifications before marking as read
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        # Mark all as read
        updated_count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # Get updated queryset
            queryset = Notification.objects.filter(user=request.user).order_by('-created_at')
            
            # Render the updated list
            context = {
                'notifications': queryset,
            }
            html = render_to_string(
                "partials/notification_list.html",
                context,
                request=request,
            )
            
            return JsonResponse({
                "success": True,
                "updated_count": updated_count,
                "unread_count": unread_count,
                "has_notifications": queryset.exists(),
                "html": html,
            })
        
        messages.success(request, f"{updated_count} notifications marked as read.")
        return redirect("list")
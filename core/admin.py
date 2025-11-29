from django.contrib import admin
from .models import MediaUpload, ContactMessage

@admin.register(MediaUpload)
class MediaUploadAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'media_type', 'uploaded_at', 'is_active']
    list_filter = ['media_type', 'uploaded_at', 'is_active']
    search_fields = ['title', 'description', 'user__username']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'status']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']

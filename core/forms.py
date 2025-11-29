from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MediaUpload, ContactMessage

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = MediaUpload
        fields = ['title', 'description', 'media_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a title for your media'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your media...'}),
            'media_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_media_file(self):
        media_file = self.cleaned_data.get('media_file')
        if media_file:
            # Check file size (500MB limit for videos, 50MB for images)
            max_size = 500 * 1024 * 1024  # 500MB
            
            if media_file.size > max_size:
                raise forms.ValidationError(f"File size must be under 500MB. Your file is {media_file.size / (1024*1024):.1f}MB")
            
            # Check file type
            content_type = media_file.content_type
            allowed_types = [
                'image/jpeg', 'image/png', 'image/gif', 'image/webp',
                'video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-msvideo',
                'video/x-ms-wmv', 'video/webm'
            ]
            
            if content_type not in allowed_types:
                raise forms.ValidationError("Please upload only images (JPEG, PNG, GIF, WebP) or videos (MP4, MPEG, MOV, AVI, WMV, WebM)")
        
        return media_file

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email address'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject of your message'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your message...'}),
        }

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from .models import MediaUpload, ContactMessage
from .forms import CustomUserCreationForm, MediaUploadForm, ContactForm

@login_required
def index(request):
    return render(request, 'core/index.html')

@login_required
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save()
            
            # Send email notification (in production)
            if not settings.DEBUG:
                try:
                    send_mail(
                        f'New Contact Message: {contact_msg.subject}',
                        f'Name: {contact_msg.name}\nEmail: {contact_msg.email}\nMessage: {contact_msg.message}',
                        settings.DEFAULT_FROM_EMAIL,
                        [settings.EMAIL_HOST_USER],  # Send to admin email
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Email sending failed: {e}")
            
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})

@login_required
def gallery(request):
    uploads_list = MediaUpload.objects.filter(is_active=True).select_related('user').order_by('-uploaded_at')
    paginator = Paginator(uploads_list, 9)  # Show 9 items per page
    page_number = request.GET.get('page')
    uploads = paginator.get_page(page_number)
    return render(request, 'core/gallery.html', {'uploads': uploads})

def register(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html')

@login_required
def upload_media(request):
    if request.method == 'POST':
        form = MediaUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user
            
            # Determine media type
            file = request.FILES['media_file']
            if file.content_type.startswith('image'):
                upload.media_type = 'image'
            elif file.content_type.startswith('video'):
                upload.media_type = 'video'
            else:
                messages.error(request, 'Unsupported file type. Please upload images or videos only.')
                return render(request, 'core/upload.html', {'form': form})
            
            upload.save()
            messages.success(request, 'Media uploaded successfully!')
            return redirect('gallery')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MediaUploadForm()
    return render(request, 'core/upload.html', {'form': form})

def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
@login_required
def admin_dashboard(request):
    uploads = MediaUpload.objects.all().select_related('user')
    active_messages = ContactMessage.objects.exclude(status='archived')
    archived_messages = ContactMessage.objects.filter(status='archived')
    
    if request.method == 'POST':
        if 'delete_upload' in request.POST:
            upload_id = request.POST.get('delete_upload')
            upload = get_object_or_404(MediaUpload, id=upload_id)
            upload.delete()
            messages.success(request, 'Upload deleted successfully!')
            return redirect('admin_dashboard')
        
        elif 'mark_read' in request.POST:
            message_id = request.POST.get('mark_read')
            message = get_object_or_404(ContactMessage, id=message_id)
            message.mark_as_read()
            messages.success(request, 'Message marked as read!')
            return redirect('admin_dashboard#messages')
        
        elif 'archive_message' in request.POST:
            message_id = request.POST.get('archive_message')
            message = get_object_or_404(ContactMessage, id=message_id)
            message.archive()
            messages.success(request, 'Message archived!')
            return redirect('admin_dashboard#messages')
        
        elif 'restore_message' in request.POST:
            message_id = request.POST.get('restore_message')
            message = get_object_or_404(ContactMessage, id=message_id)
            message.restore()
            messages.success(request, 'Message restored!')
            return redirect('admin_dashboard#archived')
        
        elif 'delete_message' in request.POST:
            message_id = request.POST.get('delete_message')
            message = get_object_or_404(ContactMessage, id=message_id)
            message.delete()
            messages.success(request, 'Message deleted permanently!')
            # Redirect to appropriate tab
            if 'archived' in request.META.get('HTTP_REFERER', ''):
                return redirect('admin_dashboard#archived')
            else:
                return redirect('admin_dashboard#messages')
    
    return render(request, 'core/admin_dashboard.html', {
        'uploads': uploads,
        'active_messages': active_messages,
        'archived_messages': archived_messages
    })

@require_POST
@csrf_exempt
def mark_message_read(request, message_id):
    if request.user.is_authenticated and request.user.is_staff:
        message = get_object_or_404(ContactMessage, id=message_id)
        message.mark_as_read()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=403)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
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
            contact_msg = form.save(commit=False)
            contact_msg.save()
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})

@login_required
def gallery(request):
    uploads = MediaUpload.objects.filter(is_active=True)
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
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
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
            file_type = request.FILES['media_file'].content_type.split('/')[0]
            upload.media_type = 'video' if file_type == 'video' else 'image'
            
            upload.save()
            messages.success(request, 'Media uploaded successfully!')
            return redirect('gallery')
    else:
        form = MediaUploadForm()
    return render(request, 'core/upload.html', {'form': form})

def is_admin(user):
    return user.is_staff

@user_passes_test(is_admin)
@login_required
def admin_dashboard(request):
    uploads = MediaUpload.objects.all()
    contact_messages = ContactMessage.objects.all()
    
    if request.method == 'POST' and 'delete_upload' in request.POST:
        upload_id = request.POST.get('delete_upload')
        upload = get_object_or_404(MediaUpload, id=upload_id)
        upload.delete()
        messages.success(request, 'Upload deleted successfully!')
        return redirect('admin_dashboard')
    
    return render(request, 'core/admin_dashboard.html', {
        'uploads': uploads,
        'contact_messages': contact_messages
    })


# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse, Http404
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta
import os
from .models import AdminProfile, Visit, Download, AnalyticsSummary
from django.contrib.auth import get_user_model
from django.db.models import Q as ORM_Q
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        identifier = (request.POST.get('email') or request.POST.get('username') or '').strip()
        password = (request.POST.get('password') or '').strip()

        if identifier and password:
            # Allow login by email or username
            user_obj = None
            try:
                # Prefer email if identifier looks like an email
                if '@' in identifier:
                    user_obj = User.objects.filter(email__iexact=identifier).first()
                if user_obj is None:
                    user_obj = User.objects.filter(username__iexact=identifier).first()
            except Exception:
                user_obj = None

            username_for_auth = user_obj.username if user_obj else identifier

            user = authenticate(request, username=username_for_auth, password=password)
            if user is not None:
                login(request, user)
                # Role-based redirect
                if user.is_staff or user.is_superuser:
                    return redirect('dashboard')
                return redirect('account_profile')
            else:
                messages.error(request, 'Invalid email/username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')

    return render(request, "login.html")

def register_view(request):
    if request.method == 'POST':
        # Build a UserCreationForm with the required username/password fields
        form = UserCreationForm(request.POST)
        # Validate both the Django form and custom fields we expect from the Arrowroot template
        required_custom_fields = ['first_name', 'last_name', 'email']
        missing = [f for f in required_custom_fields if not request.POST.get(f)]
        if form.is_valid() and not missing:
            user = form.save(commit=False)
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            for f in missing:
                messages.error(request, f"{f}: This field is required")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})

@login_required
def dashboard(request):
    try:
        admin_profile = AdminProfile.objects.get(user=request.user)
        is_admin = admin_profile.is_admin
    except AdminProfile.DoesNotExist:
        is_admin = False
    
    context = {
        'user': request.user,
        'is_admin': is_admin,
    }
    # Only admins/staff should see dashboard; others go to account profile
    if not (request.user.is_staff or request.user.is_superuser or is_admin):
        return redirect('account_profile')
    return render(request, "admin/dashboard.html", context)

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

def home(request):
    # Always show marketing/landing home page at root
    return render(request, "home.html")

@login_required
def account_profile(request):
    return render(request, "accountprofile.html", {"user": request.user})

@login_required
def planting_view(request):
    return render(request, "planting.html")

@login_required
def cultural_view(request):
    return render(request, "cultural.html")

@login_required
def historical_view(request):
    return render(request, "historical.html")

@login_required
def economic_view(request):
    return render(request, "economic.html")

@login_required
def track_download(request, file_name):
    """Track file downloads and serve the file"""
    try:
        # Admin/staff only
        try:
            admin_profile = AdminProfile.objects.get(user=request.user)
            is_admin = admin_profile.is_admin
        except AdminProfile.DoesNotExist:
            is_admin = False
        if not (request.user.is_staff or request.user.is_superuser or is_admin):
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('account_profile')
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Get session ID
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # Create download record
        Download.objects.create(
            file_name=file_name,
            file_path=f"/downloads/{file_name}",
            file_size=0,  # You can calculate actual file size
            user=request.user if request.user.is_authenticated else None,
            ip_address=ip,
            user_agent=user_agent,
            session_id=session_id
        )
        
        # For demo purposes, return a simple text file
        response = HttpResponse(f"This is a demo download file: {file_name}\nDownloaded at: {timezone.now()}")
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
        
    except Exception as e:
        messages.error(request, f"Download error: {e}")
        return redirect('dashboard')

@login_required
def analytics_dashboard(request):
    """Analytics dashboard with charts and statistics"""
    try:
        admin_profile = AdminProfile.objects.get(user=request.user)
        is_admin = admin_profile.is_admin
    except AdminProfile.DoesNotExist:
        is_admin = False
    
    if not (request.user.is_staff or request.user.is_superuser or is_admin):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('account_profile')
    
    # Get date range (last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Get visit statistics
    visits = Visit.objects.filter(timestamp__date__range=[start_date, end_date])
    downloads = Download.objects.filter(timestamp__date__range=[start_date, end_date])
    
    # Daily statistics
    daily_visits = visits.extra(
        select={'day': 'date(timestamp)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    daily_downloads = downloads.extra(
        select={'day': 'date(timestamp)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Top pages
    top_pages = visits.values('page_url').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Top downloads
    top_downloads = downloads.values('file_name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Recent activity
    recent_visits = visits[:20]
    recent_downloads = downloads[:20]
    
    # Summary statistics
    total_visits = visits.count()
    unique_visitors = visits.values('ip_address').distinct().count()
    total_downloads = downloads.count()
    unique_downloaders = downloads.values('ip_address').distinct().count()
    
    context = {
        'user': request.user,
        'is_admin': is_admin,
        'total_visits': total_visits,
        'unique_visitors': unique_visitors,
        'total_downloads': total_downloads,
        'unique_downloaders': unique_downloaders,
        'daily_visits': list(daily_visits),
        'daily_downloads': list(daily_downloads),
        'top_pages': list(top_pages),
        'top_downloads': list(top_downloads),
        'recent_visits': recent_visits,
        'recent_downloads': recent_downloads,
        'date_range': f"{start_date} to {end_date}"
    }
    
    return render(request, "analytics.html", context)



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

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, "login.html")

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
    return render(request, "dashboard.html", context)

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

def track_download(request, file_name):
    """Track file downloads and serve the file"""
    try:
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
    
    if not is_admin:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    
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


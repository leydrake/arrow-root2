from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import Visit
import hashlib

class AnalyticsMiddleware(MiddlewareMixin):
    """Middleware to automatically track user visits"""
    
    def process_request(self, request):
        # Skip tracking for certain paths
        skip_paths = [
            '/admin/',
            '/static/',
            '/favicon.ico',
            '/analytics/',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Get referer
        referer = request.META.get('HTTP_REFERER', '')
        
        # Get session ID
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        
        # Create visit record
        try:
            Visit.objects.create(
                ip_address=ip,
                user_agent=user_agent,
                page_url=request.build_absolute_uri(),
                referer=referer if referer else None,
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id
            )
        except Exception as e:
            # Log error but don't break the request
            print(f"Analytics tracking error: {e}")
        
        return None


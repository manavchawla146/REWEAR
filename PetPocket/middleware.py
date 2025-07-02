# middleware.py

from flask import request, g
from flask_login import current_user
from .models import db, PageView, ProductView, ProductAnalytics
import re
from datetime import datetime

class AnalyticsMiddleware:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        g.request_start_time = datetime.utcnow()
    
    def after_request(self, response):
        # Skip static files and admin routes
        if request.path.startswith('/static') or request.path.startswith('/admin'):
            return response
        
        # Get the IP address
        ip_address = request.remote_addr
        
        # Get user id if logged in
        user_id = current_user.id if current_user.is_authenticated else None
        
        # Log the page view
        page_view = PageView(
            page=request.path,
            ip_address=ip_address,
            user_id=user_id,
            user_agent=request.user_agent.string,
            timestamp=g.request_start_time
        )
        
        # Check if it's a product view
        product_id = self._extract_product_id(request.path)
        if product_id:
            product_view = ProductView(
                product_id=product_id,
                user_id=user_id,
                ip_address=ip_address,
                timestamp=g.request_start_time
            )
            db.session.add(product_view)
            
            # Update product analytics
            ProductAnalytics.increment_view(product_id)
        
        # Commit the changes to the database
        try:
            db.session.add(page_view)
            db.session.commit()
        except Exception as e:
            # Log the error, but don't disrupt the request
            print(f"Error recording analytics: {str(e)}")
            db.session.rollback()
        
        return response
    
    def _extract_product_id(self, path):
        """Extract product ID from various URL patterns"""
        # Product detail page pattern
        product_pattern = re.compile(r'/product(?:s)?/(\d+)')
        product_match = product_pattern.match(path)
        if product_match:
            return int(product_match.group(1))
        
        # API product detail pattern
        api_pattern = re.compile(r'/get_product_details/(\d+)')
        api_match = api_pattern.match(path)
        if api_match:
            return int(api_match.group(1))
        
        return None
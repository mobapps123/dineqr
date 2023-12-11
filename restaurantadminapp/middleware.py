from django.conf import settings
from django.urls import resolve

class CustomSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URL names for which to set custom session settings
        custom_url_names = ['mobile_home', 'mobile_items', 'AddToCartView','success-page','mob_Item_details']

        # Get the URL name for the current request
        resolved_url = resolve(request.path_info)
        url_name = resolved_url.url_name if resolved_url.url_name else ''

        # Check if the URL name matches any custom names
        if url_name in custom_url_names:
            request.session.set_expiry(60*20)  # Set expiration to 30 minutes

        response = self.get_response(request)
        return response
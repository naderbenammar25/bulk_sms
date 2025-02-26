import pytz
from django.utils import timezone

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_timezone = request.user.timezone
            if user_timezone and user_timezone != 'Automatique':
                timezone.activate(pytz.timezone(user_timezone))
            else:
                timezone.deactivate()
        else:
            timezone.deactivate()
        response = self.get_response(request)
        return response
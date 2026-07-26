from rest_framework.views import exception_handler
from rest_framework.exceptions import AuthenticationFailed

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        # Ensure error messages are in the { "detail": "..." } format
        if 'detail' not in response.data:
            response.data = {'detail': response.data}
        # If it's a 401, we can let the frontend handle refresh
    return response
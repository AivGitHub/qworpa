from datetime import datetime

from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None and 'detail' in response.data:
        response.data['time'] = datetime.now()
        response.data['message'] = response.data['detail']
        del response.data['detail']
    print(response)
    return response

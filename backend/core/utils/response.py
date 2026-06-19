"""
Standardized API response utilities.
"""
from rest_framework.response import Response
from rest_framework import status
from typing import Any, Dict, Optional


def success_response(
    data: Any = None,
    message: str = 'Success',
    status_code: int = status.HTTP_200_OK,
    meta: Optional[Dict] = None
) -> Response:
    """Create a standardized success response."""
    response_data = {
        'success': True,
        'message': message,
        'data': data,
    }
    if meta:
        response_data['meta'] = meta
    return Response(response_data, status=status_code)


def error_response(
    message: str = 'An error occurred',
    errors: Any = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> Response:
    """Create a standardized error response."""
    response_data = {
        'success': False,
        'message': message,
    }
    if errors:
        response_data['errors'] = errors
    return Response(response_data, status=status_code)


def paginated_response(
    queryset,
    serializer_class,
    request,
    context: Optional[Dict] = None
) -> Response:
    """Create a paginated response."""
    from rest_framework.pagination import PageNumberPagination
    
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)
    
    if page is not None:
        serializer = serializer_class(page, many=True, context=context)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = serializer_class(queryset, many=True, context=context)
    return success_response(data=serializer.data)

from rest_framework.exceptions import APIException
from rest_framework import status


class CustomAPIException(APIException):
    """Base custom exception for API"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A server error occurred.'


class ValidationError(CustomAPIException):
    """Validation error"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid data provided.'


class NotFoundError(CustomAPIException):
    """Resource not found"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'


class PermissionError(CustomAPIException):
    """Permission denied"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'


class RateLimitError(CustomAPIException):
    """Rate limit exceeded"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded. Please try again later.'


class PaymentError(CustomAPIException):
    """Payment processing error"""
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'Payment processing failed.'


class OutOfStockError(CustomAPIException):
    """Product out of stock"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Product is out of stock.'

"""
Data Validation Algorithms and Utilities

Provides efficient validation algorithms for:
- Price validation
- Inventory validation
- Email/phone validation
- Data constraint checking
"""

import re
from decimal import Decimal
from typing import Tuple
from django.core.exceptions import ValidationError


# Legacy Django validators (kept for backward compatibility)
def validate_phone_number(value):
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    if not re.match(pattern, value.replace(' ', '').replace('-', '')):
        raise ValidationError('Invalid phone number format.')


def validate_postal_code(value):
    """Validate postal code format"""
    pattern = r'^\d{5}(-\d{4})?$'
    if not re.match(pattern, value):
        raise ValidationError('Invalid postal code format.')


def validate_product_sku(value):
    """Validate SKU format"""
    pattern = r'^[A-Z0-9-]+$'
    if not re.match(pattern, value):
        raise ValidationError('SKU must contain only uppercase letters, numbers, and hyphens.')


# ============================================================================
# NEW: Efficient Validation Algorithms
# ============================================================================

class PriceValidator:
    """Validates price-related operations"""
    
    MIN_PRICE = Decimal('0.00')
    MAX_PRICE = Decimal('999999.99')
    
    @staticmethod
     
    def validate_price(price: Decimal) -> Tuple[bool, str]:
        """
        Validate product price.
        
        Algorithm: Range validation with precision check.
        
        Args:
            price: Price to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            price_val = Decimal(str(price))
        except Exception:
            return False, "Invalid price format"
        
        if price_val < PriceValidator.MIN_PRICE:
            return False, "Price cannot be negative"
        
        if price_val > PriceValidator.MAX_PRICE:
            return False, f"Price exceeds maximum ({PriceValidator.MAX_PRICE})"
        
        # Check decimal places
        if price_val.as_tuple().exponent < -2:
            return False, "Price can have maximum 2 decimal places"
        
        return True, ""


class InventoryValidator:
    """Validates inventory operations"""
    
    MIN_QUANTITY = 0
    MAX_QUANTITY = 999999
    
    @staticmethod
    def validate_quantity(quantity: int) -> Tuple[bool, str]:
        """
        Validate product quantity.
        
        Algorithm: Range validation.
        
        Args:
            quantity: Quantity to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            qty = int(quantity)
        except (ValueError, TypeError):
            return False, "Quantity must be an integer"
        
        if qty < InventoryValidator.MIN_QUANTITY:
            return False, "Quantity cannot be negative"
        
        if qty > InventoryValidator.MAX_QUANTITY:
            return False, f"Quantity exceeds maximum ({InventoryValidator.MAX_QUANTITY})"
        
        return True, ""
    
    @staticmethod
    def validate_order_quantity(available: int, requested: int) -> Tuple[bool, str]:
        """
        Validate order quantity against available stock.
        
        Algorithm: Availability check.
        
        Args:
            available: Available quantity
            requested: Requested quantity
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if requested <= 0:
            return False, "Quantity must be greater than 0"
        
        if requested > available:
            return False, f"Only {available} units available"
        
        return True, ""


class EmailValidator:
    """Validates email addresses"""
    
    # RFC 5322 simplified email regex
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email address format.
        
        Algorithm: Regex pattern matching (O(n) where n is email length).
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email or not isinstance(email, str):
            return False, "Email is required"
        
        email = email.strip().lower()
        
        if len(email) > 254:
            return False, "Email is too long"
        
        if not EmailValidator.EMAIL_PATTERN.match(email):
            return False, "Invalid email format"
        
        return True, ""


class AddressValidator:
    """Validates address information"""
    
    REQUIRED_FIELDS = ['street_address', 'city', 'country', 'zip_code']
    
    @staticmethod
    def validate_address(address_data: dict) -> Tuple[bool, list]:
        """
        Validate complete address data.
        
        Algorithm: Field-by-field validation with error collection.
        
        Args:
            address_data: Dictionary with address fields
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        for field in AddressValidator.REQUIRED_FIELDS:
            if not address_data.get(field) or not str(address_data.get(field)).strip():
                errors.append(f"{field} is required")
        
        # Validate individual fields
        if address_data.get('street_address'):
            if len(address_data.get('street_address', '')) > 200:
                errors.append("Street address is too long")
        
        if address_data.get('city'):
            if len(address_data.get('city', '')) > 100:
                errors.append("City is too long")
        
        if address_data.get('zip_code'):
            zip_code = str(address_data.get('zip_code', '')).strip()
            if not re.match(r'^[a-zA-Z0-9\s\-]{3,10}$', zip_code):
                errors.append("Invalid zip/postal code format")
        
        if address_data.get('phone_number'):
            phone = address_data.get('phone_number')
            if phone:
                if len(phone) > 20:
                    errors.append("Phone number is too long")
                elif not re.match(r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,9}$', phone):
                    errors.append("Invalid phone number format")
        
        return len(errors) == 0, errors


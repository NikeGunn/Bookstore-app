from rest_framework import serializers
from .models import Book


# Error Response Serializers for OpenAPI documentation
class ErrorResponseSerializer(serializers.Serializer):
    """Generic error response serializer"""
    success = serializers.BooleanField(default=False)
    message = serializers.CharField()


class ValidationErrorResponseSerializer(serializers.Serializer):
    """Validation error response serializer"""
    success = serializers.BooleanField(default=False)
    message = serializers.CharField()
    errors = serializers.DictField(child=serializers.ListField(child=serializers.CharField()))


class NotFoundErrorResponseSerializer(serializers.Serializer):
    """Not found error response serializer"""
    success = serializers.BooleanField(default=False)
    message = serializers.CharField(default="Book not found")


class SuccessResponseSerializer(serializers.Serializer):
    """Success response serializer"""
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()


class BookStatsSerializer(serializers.Serializer):
    """Serializer for book statistics"""
    total_books = serializers.IntegerField()
    total_stock = serializers.IntegerField()
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    genres = serializers.ListField(child=serializers.CharField())


class BookSerializer(serializers.ModelSerializer):
    """Serializer for Book model - used for read operations"""

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn', 'published_year',
            'genre', 'price', 'stock', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new books"""

    class Meta:
        model = Book
        fields = [
            'title', 'author', 'isbn', 'published_year',
            'genre', 'price', 'stock', 'description'
        ]

    def validate_title(self, value):
        """Validate title field"""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty or contain only whitespace.")
        return value.strip()

    def validate_author(self, value):
        """Validate author field"""
        if not value or not value.strip():
            raise serializers.ValidationError("Author cannot be empty or contain only whitespace.")
        return value.strip()

    def validate_genre(self, value):
        """Validate genre field"""
        if not value or not value.strip():
            raise serializers.ValidationError("Genre cannot be empty or contain only whitespace.")
        return value.strip()

    def validate_isbn(self, value):
        """Validate ISBN uniqueness"""
        if Book.objects.filter(isbn=value).exists():
            raise serializers.ValidationError(f"A book with ISBN {value} already exists.")
        return value


class BookUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating existing books"""

    class Meta:
        model = Book
        fields = [
            'title', 'author', 'isbn', 'published_year',
            'genre', 'price', 'stock', 'description'
        ]

    def validate_title(self, value):
        """Validate title field"""
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError("Title cannot be empty or contain only whitespace.")
        return value.strip() if value else value

    def validate_author(self, value):
        """Validate author field"""
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError("Author cannot be empty or contain only whitespace.")
        return value.strip() if value else value

    def validate_genre(self, value):
        """Validate genre field"""
        if value is not None and (not value or not value.strip()):
            raise serializers.ValidationError("Genre cannot be empty or contain only whitespace.")
        return value.strip() if value else value

    def validate_isbn(self, value):
        """Validate ISBN uniqueness for updates"""
        if value and Book.objects.filter(isbn=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError(f"A book with ISBN {value} already exists.")
        return value

    def validate(self, attrs):
        """Ensure at least one field is provided for update"""
        if not attrs:
            raise serializers.ValidationError("At least one field must be provided for update.")
        return attrs

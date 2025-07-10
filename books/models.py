import uuid
import re
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError


def validate_isbn(value):
    """Custom validator for ISBN format"""
    isbn_pattern = r'^(?:ISBN(?:-1[03])?:? )?(?=[0-9X]{10}$|(?=(?:[0-9]+[- ]){3})[- 0-9X]{13}$|97[89][0-9]{10}$|(?=(?:[0-9]+[- ]){4})[- 0-9]{17}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?[0-9]+[- ]?[0-9]+[- ]?[0-9X]$'
    if not re.match(isbn_pattern, value):
        raise ValidationError('Invalid ISBN format. Please provide a valid ISBN-10 or ISBN-13.')


class Book(models.Model):
    """Book model representing a book in the bookstore"""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the book"
    )

    title = models.CharField(
        max_length=200,
        help_text="Title of the book"
    )

    author = models.CharField(
        max_length=100,
        help_text="Author of the book"
    )

    isbn = models.CharField(
        max_length=17,
        unique=True,
        validators=[validate_isbn],
        help_text="ISBN-10 or ISBN-13 of the book"
    )

    published_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1000, message="Published year must be at least 1000"),
            MaxValueValidator(2025, message="Published year cannot be more than 2025")
        ],
        help_text="Year the book was published"
    )

    genre = models.CharField(
        max_length=50,
        help_text="Genre of the book"
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message="Price must be at least $0.01")],
        help_text="Price of the book in USD"
    )

    stock = models.PositiveIntegerField(
        default=0,
        help_text="Number of books in stock"
    )

    description = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="Description of the book"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the book was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the book was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['genre']),
            models.Index(fields=['isbn']),
        ]
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return f"{self.title} by {self.author}"

    def clean(self):
        """Custom validation for the model"""
        super().clean()

        # Ensure title and author are not empty
        if not self.title or not self.title.strip():
            raise ValidationError({'title': 'Title cannot be empty or contain only whitespace.'})

        if not self.author or not self.author.strip():
            raise ValidationError({'author': 'Author cannot be empty or contain only whitespace.'})

        if not self.genre or not self.genre.strip():
            raise ValidationError({'genre': 'Genre cannot be empty or contain only whitespace.'})

    def save(self, *args, **kwargs):
        """Override save to call clean()"""
        self.clean()
        super().save(*args, **kwargs)

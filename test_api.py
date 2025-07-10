#!/usr/bin/env python
"""
Test script for the Bookstore API
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append('c:\\Users\\Nautilus\\Desktop\\New folder')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore_api.settings')
django.setup()

from books.models import Book
from decimal import Decimal


def create_sample_data():
    """Create sample books for testing"""
    sample_books = [
        {
            'title': 'The Great Gatsby',
            'author': 'F. Scott Fitzgerald',
            'isbn': '978-0-7432-7356-5',
            'published_year': 1925,
            'genre': 'Fiction',
            'price': Decimal('12.99'),
            'stock': 50,
            'description': 'A classic American novel set in the Jazz Age.'
        },
        {
            'title': 'To Kill a Mockingbird',
            'author': 'Harper Lee',
            'isbn': '978-0-06-112008-4',
            'published_year': 1960,
            'genre': 'Fiction',
            'price': Decimal('14.99'),
            'stock': 30,
            'description': 'A gripping tale of racial injustice and childhood innocence.'
        },
        {
            'title': '1984',
            'author': 'George Orwell',
            'isbn': '978-0-452-28423-4',
            'published_year': 1949,
            'genre': 'Dystopian Fiction',
            'price': Decimal('13.99'),
            'stock': 40,
            'description': 'A dystopian social science fiction novel.'
        },
        {
            'title': 'Pride and Prejudice',
            'author': 'Jane Austen',
            'isbn': '978-0-14-143951-8',
            'published_year': 1813,
            'genre': 'Romance',
            'price': Decimal('11.99'),
            'stock': 25,
            'description': 'A romantic novel about manners and marriage.'
        },
        {
            'title': 'The Catcher in the Rye',
            'author': 'J.D. Salinger',
            'isbn': '978-0-316-76948-0',
            'published_year': 1951,
            'genre': 'Fiction',
            'price': Decimal('15.99'),
            'stock': 35,
            'description': 'A coming-of-age story in New York City.'
        }
    ]

    created_count = 0
    for book_data in sample_books:
        book, created = Book.objects.get_or_create(
            isbn=book_data['isbn'],
            defaults=book_data
        )
        if created:
            created_count += 1
            print(f'✓ Created book: {book.title}')
        else:
            print(f'⚠ Book already exists: {book.title}')

    print(f'\n🎉 Sample data creation completed. {created_count} new books created.')
    print(f'📊 Total books in database: {Book.objects.count()}')


def test_api_endpoints():
    """Test the API functionality"""
    print("\n🔍 Testing API functionality...")

    # Test model validation
    try:
        total_books = Book.objects.count()
        print(f"✓ Database connection working. Found {total_books} books.")

        # Test a single book
        if total_books > 0:
            book = Book.objects.first()
            print(f"✓ Sample book: '{book.title}' by {book.author}")
            print(f"  📖 ISBN: {book.isbn}")
            print(f"  💰 Price: ${book.price}")
            print(f"  📦 Stock: {book.stock}")

    except Exception as e:
        print(f"❌ Database error: {e}")


def show_api_info():
    """Show API information"""
    print("\n🌐 Bookstore API Information")
    print("=" * 50)
    print("📝 API Documentation: http://localhost:8000/api/docs/")
    print("📚 Redoc Documentation: http://localhost:8000/api/redoc/")
    print("🔍 API Schema: http://localhost:8000/api/schema/")
    print("🏥 Health Check: http://localhost:8000/health/")
    print("\n📋 Available Endpoints:")
    print("• GET    /api/v1/books/           - List all books")
    print("• POST   /api/v1/books/           - Create a new book")
    print("• GET    /api/v1/books/{id}/      - Get a specific book")
    print("• PUT    /api/v1/books/{id}/      - Update a book completely")
    print("• PATCH  /api/v1/books/{id}/      - Update a book partially")
    print("• DELETE /api/v1/books/{id}/      - Delete a book")
    print("• GET    /api/v1/books/stats/     - Get bookstore statistics")
    print("\n🚀 To start the server: python manage.py runserver")


if __name__ == '__main__':
    print("🚀 Bookstore API Setup & Test")
    print("=" * 50)

    create_sample_data()
    test_api_endpoints()
    show_api_info()

"""
Bookstore API - Complete Django REST Framework Implementation
===========================================================

This is a comprehensive Django REST API for bookstore management with:
- Full CRUD operations for books
- DRF Spectacular for OpenAPI/Swagger documentation
- Advanced filtering and searching
- Proper error handling and validation
- Django admin interface

🚀 Quick Start:
1. python manage.py runserver
2. Visit http://localhost:8000/api/docs/ for interactive documentation

📋 API Endpoints:
- GET    /api/v1/books/           - List all books with filtering/pagination
- POST   /api/v1/books/           - Create a new book
- GET    /api/v1/books/{id}/      - Get a specific book
- PUT    /api/v1/books/{id}/      - Update a book completely
- PATCH  /api/v1/books/{id}/      - Update a book partially
- DELETE /api/v1/books/{id}/      - Delete a book
- GET    /api/v1/books/stats/     - Get bookstore statistics

📖 Documentation:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/
- Django Admin: http://localhost:8000/admin/

✨ Features:
- UUID primary keys
- ISBN validation
- Advanced filtering (price range, year range, stock status)
- Search across title, author, genre, description
- Pagination support
- Comprehensive error responses
- CORS support for frontend integration

Example API Usage:

# List all books
curl -X GET "http://localhost:8000/api/v1/books/"

# Search books by title
curl -X GET "http://localhost:8000/api/v1/books/?search=gatsby"

# Filter by genre and price range
curl -X GET "http://localhost:8000/api/v1/books/?genre=fiction&price_min=10&price_max=20"

# Create a new book
curl -X POST "http://localhost:8000/api/v1/books/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "New Book",
       "author": "Author Name",
       "isbn": "978-0-123456-78-9",
       "published_year": 2023,
       "genre": "Fiction",
       "price": 19.99,
       "stock": 10,
       "description": "A great new book"
     }'

# Get statistics
curl -X GET "http://localhost:8000/api/v1/books/stats/"

The API follows the same structure as your Node.js implementation but with Django/DRF best practices.
"""

import os
import sys
import django

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore_api.settings')
django.setup()

from books.models import Book


def main():
    print(__doc__)

    print("\n" + "="*60)
    print("📊 Current Database Status:")
    print("="*60)

    total_books = Book.objects.count()
    print(f"Total books in database: {total_books}")

    if total_books > 0:
        print("\n📚 Sample books in the database:")
        for book in Book.objects.all()[:3]:
            print(f"• {book.title} by {book.author} (${book.price})")

        if total_books > 3:
            print(f"... and {total_books - 3} more books")

    print("\n🚀 Ready to use! Start the server with: python manage.py runserver")


if __name__ == '__main__':
    main()

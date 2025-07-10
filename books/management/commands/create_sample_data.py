from django.core.management.base import BaseCommand
from books.models import Book
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample books for testing the API'

    def handle(self, *args, **options):
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
                self.stdout.write(
                    self.style.SUCCESS(f'Created book: {book.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Book already exists: {book.title}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSample data creation completed. '
                f'{created_count} new books created.'
            )
        )

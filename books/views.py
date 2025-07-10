from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
import logging

from .models import Book
from .serializers import (
    BookSerializer, BookCreateSerializer, BookUpdateSerializer,
    ErrorResponseSerializer, ValidationErrorResponseSerializer,
    NotFoundErrorResponseSerializer, SuccessResponseSerializer,
    BookStatsSerializer
)
from .filters import BookFilter

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="Get all books",
        description="Retrieve a paginated list of all books with optional filtering and searching.",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in title, author, genre, and description fields'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Order by: title, author, published_year, price, stock, created_at, updated_at (prefix with - for descending)'
            ),
            OpenApiParameter(
                name='title',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by title (case-insensitive)'
            ),
            OpenApiParameter(
                name='author',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by author (case-insensitive)'
            ),
            OpenApiParameter(
                name='genre',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by genre (case-insensitive)'
            ),
            OpenApiParameter(
                name='price_min',
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
                description='Minimum price filter'
            ),
            OpenApiParameter(
                name='price_max',
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
                description='Maximum price filter'
            ),
            OpenApiParameter(
                name='published_year_min',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Minimum published year filter'
            ),
            OpenApiParameter(
                name='published_year_max',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Maximum published year filter'
            ),
            OpenApiParameter(
                name='in_stock',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter books in stock (true) or out of stock (false)'
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=BookSerializer(many=True),
                description="List of books retrieved successfully"
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad request - invalid parameters"
            ),
            500: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Internal server error"
            )
        },
        tags=['Books']
    ),
    create=extend_schema(
        summary="Create a new book",
        description="Add a new book to the bookstore inventory.",
        request=BookCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=BookSerializer,
                description="Book created successfully"
            ),
            400: OpenApiResponse(
                response=ValidationErrorResponseSerializer,
                description="Bad request - validation errors"
            ),
            409: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Conflict - book with same ISBN already exists"
            ),
            500: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Internal server error"
            )
        },
        tags=['Books']
    ),
    retrieve=extend_schema(
        summary="Get a specific book",
        description="Retrieve detailed information about a specific book by its ID.",
        responses={
            200: OpenApiResponse(
                response=BookSerializer,
                description="Book details retrieved successfully"
            ),
            404: OpenApiResponse(
                response=NotFoundErrorResponseSerializer,
                description="Book not found"
            ),
            500: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Internal server error"
            )        },
        tags=['Books']
    ),
    update=extend_schema(
        summary="Update a book completely",
        description="Update all fields of an existing book.",
        request=BookUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=BookSerializer,
                description="Book updated successfully"
            ),
            400: OpenApiResponse(
                response=ValidationErrorResponseSerializer,
                description="Bad request - validation errors"
            ),
            404: OpenApiResponse(
                response=NotFoundErrorResponseSerializer,
                description="Book not found"
            ),
            409: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Conflict - ISBN already exists"
            ),
            500: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Internal server error"
            )
        },
        tags=['Books']
    ),    partial_update=extend_schema(
        summary="Update a book partially",
        description="Update specific fields of an existing book.",
        request=BookUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=BookSerializer,
                description="Book updated successfully"
            ),
            400: OpenApiResponse(
                response=ValidationErrorResponseSerializer,
                description="Bad request - validation errors"
            ),
            404: OpenApiResponse(
                response=NotFoundErrorResponseSerializer,
                description="Book not found"
            ),
            409: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Conflict - ISBN already exists"
            ),
            500: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Internal server error"
            )
        },
        tags=['Books']
    ),    destroy=extend_schema(
        summary="Delete a book",
        description="Remove a book from the bookstore inventory.",
        responses={
            204: OpenApiResponse(
                description="Book deleted successfully"
            ),
            404: OpenApiResponse(
                response=NotFoundErrorResponseSerializer,
                description="Book not found"
            ),
            500: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Internal server error"
            )
        },
        tags=['Books']
    ),
)
class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing books in the bookstore.

    Provides CRUD operations:
    - GET /api/v1/books/ - List all books with filtering and pagination
    - POST /api/v1/books/ - Create a new book
    - GET /api/v1/books/{id}/ - Retrieve a specific book
    - PUT /api/v1/books/{id}/ - Update a book completely
    - PATCH /api/v1/books/{id}/ - Update a book partially
    - DELETE /api/v1/books/{id}/ - Delete a book
    """

    queryset = Book.objects.all()
    filterset_class = BookFilter
    search_fields = ['title', 'author', 'genre', 'description']
    ordering_fields = ['title', 'author', 'published_year', 'price', 'stock', 'created_at', 'updated_at']
    ordering = ['-created_at']  # Default ordering

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return BookCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BookUpdateSerializer
        return BookSerializer

    def create(self, request, *args, **kwargs):
        """Create a new book with proper error handling"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            book = serializer.save()
            response_serializer = BookSerializer(book)

            logger.info(f"Book created successfully: {book.title} (ID: {book.id})")

            return Response({
                'success': True,
                'message': 'Book created successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)

        except IntegrityError as e:
            logger.error(f"Integrity error creating book: {str(e)}")
            if 'isbn' in str(e).lower():
                return Response({
                    'success': False,
                    'error': 'Book already exists',
                    'message': f'A book with this ISBN already exists'
                }, status=status.HTTP_409_CONFLICT)

            return Response({
                'success': False,
                'error': 'Database constraint violation',
                'message': 'Could not create book due to database constraints'
            }, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            logger.error(f"Validation error creating book: {str(e)}")
            return Response({
                'success': False,
                'error': 'Validation failed',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error creating book: {str(e)}")
            return Response({
                'success': False,
                'error': 'Something went wrong!',
                'message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        """List books with custom response format"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)

                # Customize the paginated response
                response.data = {
                    'success': True,
                    'message': 'Books retrieved successfully',
                    'data': response.data['results'],
                    'count': response.data['count'],
                    'next': response.data['next'],
                    'previous': response.data['previous']
                }
                return response

            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'message': 'Books retrieved successfully',
                'data': serializer.data,
                'count': len(serializer.data)
            })

        except Exception as e:
            logger.error(f"Error listing books: {str(e)}")
            return Response({
                'success': False,
                'error': 'Something went wrong!',
                'message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific book with custom response format"""
        try:
            book = self.get_object()
            serializer = self.get_serializer(book)

            return Response({
                'success': True,
                'message': 'Book retrieved successfully',
                'data': serializer.data
            })

        except Book.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Book not found',
                'message': f'No book found with ID: {kwargs.get("pk")}'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error retrieving book: {str(e)}")
            return Response({
                'success': False,
                'error': 'Something went wrong!',
                'message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """Update a book with proper error handling"""
        return self._update_book(request, partial=False)

    def partial_update(self, request, *args, **kwargs):
        """Partially update a book with proper error handling"""
        return self._update_book(request, partial=True)

    def _update_book(self, request, partial=False):
        """Common update logic for both full and partial updates"""
        try:
            book = self.get_object()
            serializer = self.get_serializer(book, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            updated_book = serializer.save()
            response_serializer = BookSerializer(updated_book)

            logger.info(f"Book updated successfully: {updated_book.title} (ID: {updated_book.id})")

            return Response({
                'success': True,
                'message': 'Book updated successfully',
                'data': response_serializer.data
            })

        except Book.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Book not found',
                'message': f'No book found with ID: {kwargs.get("pk")}'
            }, status=status.HTTP_404_NOT_FOUND)

        except IntegrityError as e:
            logger.error(f"Integrity error updating book: {str(e)}")
            if 'isbn' in str(e).lower():
                return Response({
                    'success': False,
                    'error': 'Book already exists',
                    'message': 'A book with this ISBN already exists'
                }, status=status.HTTP_409_CONFLICT)

            return Response({
                'success': False,
                'error': 'Database constraint violation',
                'message': 'Could not update book due to database constraints'
            }, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            logger.error(f"Validation error updating book: {str(e)}")
            return Response({
                'success': False,
                'error': 'Validation failed',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error updating book: {str(e)}")
            return Response({
                'success': False,
                'error': 'Something went wrong!',
                'message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """Delete a book with proper error handling"""
        try:
            book = self.get_object()
            book_title = book.title
            book_id = book.id

            book.delete()

            logger.info(f"Book deleted successfully: {book_title} (ID: {book_id})")

            return Response({
                'success': True,
                'message': 'Book deleted successfully'
            }, status=status.HTTP_204_NO_CONTENT)

        except Book.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Book not found',
                'message': f'No book found with ID: {kwargs.get("pk")}'
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error deleting book: {str(e)}")
            return Response({
                'success': False,
                'error': 'Something went wrong!',
                'message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Get books statistics",
        description="Get statistical information about the bookstore inventory.",
        responses={
            200: OpenApiResponse(
                description="Statistics retrieved successfully",
                examples={
                    'application/json': {
                        'success': True,
                        'message': 'Statistics retrieved successfully',
                        'data': {
                            'total_books': 150,
                            'total_stock': 1250,
                            'out_of_stock_books': 5,
                            'genres_count': 12,
                            'average_price': 25.99,
                            'most_expensive_book': 89.99,
                            'cheapest_book': 9.99
                        }
                    }
                }            ),
            500: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Internal server error"
            )
        },
        tags=['Books']
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get bookstore statistics"""
        try:
            from django.db.models import Count, Sum, Avg, Max, Min

            queryset = self.get_queryset()

            stats = {
                'total_books': queryset.count(),
                'total_stock': queryset.aggregate(Sum('stock'))['stock__sum'] or 0,
                'out_of_stock_books': queryset.filter(stock=0).count(),
                'genres_count': queryset.values('genre').distinct().count(),
                'average_price': float(queryset.aggregate(Avg('price'))['price__avg'] or 0),
                'most_expensive_book': float(queryset.aggregate(Max('price'))['price__max'] or 0),
                'cheapest_book': float(queryset.aggregate(Min('price'))['price__min'] or 0)
            }

            return Response({
                'success': True,
                'message': 'Statistics retrieved successfully',
                'data': stats
            })

        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return Response({
                'success': False,
                'error': 'Something went wrong!',
                'message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@extend_schema(
    summary="Health check",
    description="Simple health check endpoint to verify API is running",
    tags=["Health"],
    responses={200: OpenApiResponse(description="API is healthy")}
)
def health_check(request):
    """
    Health check endpoint for monitoring and AWS health checks
    """
    return Response(
        {"status": "healthy", "message": "API is running correctly"},
        status=status.HTTP_200_OK
    )

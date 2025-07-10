import django_filters
from .models import Book


class BookFilter(django_filters.FilterSet):
    """Filter class for Book model to enable advanced filtering"""

    # Text search filters
    title = django_filters.CharFilter(lookup_expr='icontains', help_text="Filter by title (case-insensitive)")
    author = django_filters.CharFilter(lookup_expr='icontains', help_text="Filter by author (case-insensitive)")
    genre = django_filters.CharFilter(lookup_expr='icontains', help_text="Filter by genre (case-insensitive)")
    isbn = django_filters.CharFilter(lookup_expr='exact', help_text="Filter by exact ISBN")

    # Numeric range filters
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte', help_text="Minimum price")
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte', help_text="Maximum price")
    price = django_filters.RangeFilter(help_text="Price range (e.g., 10.00-50.00)")

    published_year_min = django_filters.NumberFilter(field_name='published_year', lookup_expr='gte', help_text="Minimum published year")
    published_year_max = django_filters.NumberFilter(field_name='published_year', lookup_expr='lte', help_text="Maximum published year")
    published_year = django_filters.RangeFilter(help_text="Published year range (e.g., 2000-2023)")

    stock_min = django_filters.NumberFilter(field_name='stock', lookup_expr='gte', help_text="Minimum stock quantity")
    stock_max = django_filters.NumberFilter(field_name='stock', lookup_expr='lte', help_text="Maximum stock quantity")
    stock = django_filters.RangeFilter(help_text="Stock range")

    # Boolean filters
    in_stock = django_filters.BooleanFilter(method='filter_in_stock', help_text="Filter books that are in stock (stock > 0)")

    # Date filters
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte', help_text="Created after this date")
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte', help_text="Created before this date")
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte', help_text="Updated after this date")
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte', help_text="Updated before this date")

    class Meta:
        model = Book
        fields = {
            'title': ['exact', 'icontains'],
            'author': ['exact', 'icontains'],
            'genre': ['exact', 'icontains'],
            'isbn': ['exact'],
            'published_year': ['exact', 'gte', 'lte'],
            'price': ['exact', 'gte', 'lte'],
            'stock': ['exact', 'gte', 'lte'],
        }

    def filter_in_stock(self, queryset, name, value):
        """Custom filter method for in_stock"""
        if value is True:
            return queryset.filter(stock__gt=0)
        elif value is False:
            return queryset.filter(stock=0)
        return queryset

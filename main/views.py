from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import CarBrand, PartType, Product
from django.db.models import Q


from django.db.models import Q
from django.core.paginator import Paginator

def product_list(request):
    search_query = request.GET.get('q', '')
    brand_id = request.GET.get('brand', '')
    part_type_id = request.GET.get('type', '')
    availability = request.GET.get('available', '')
    order = request.GET.get('order', '')
    page_number = request.GET.get('page', 1)

    # -----------------------------
    # BASE QUERYSET (COMMON FILTERS)
    # -----------------------------
    base_queryset = Product.objects.all()

    if availability:
        base_queryset = base_queryset.filter(available=True)

    if search_query:
        base_queryset = base_queryset.filter(name__icontains=search_query)

    base_queryset = base_queryset.distinct()

    # -----------------------------
    # EXACT MATCHES
    # -----------------------------
    exact_queryset = base_queryset

    if brand_id:
        exact_queryset = exact_queryset.filter(car_brands__id=brand_id)

    if part_type_id:
        exact_queryset = exact_queryset.filter(part_types__id=part_type_id)

    exact_queryset = exact_queryset.distinct()

    # -----------------------------
    # POSSIBLE PARTS (Universal)
    # -----------------------------
    suggested_products = base_queryset.filter(
        car_brands__isnull=True,
        part_types__isnull=True
    ).distinct()

    # -----------------------------
    # ORDERING
    # -----------------------------
    if order == 'price_asc':
        exact_queryset = exact_queryset.order_by('price')
    elif order == 'price_desc':
        exact_queryset = exact_queryset.order_by('-price')

    # Prefetch
    exact_queryset = exact_queryset.prefetch_related(
        'car_brands', 'part_types', 'images'
    )

    suggested_products = suggested_products.prefetch_related(
        'car_brands', 'part_types', 'images'
    )

    # Pagination only for exact matches
    paginator = Paginator(exact_queryset, 24)
    page_obj = paginator.get_page(page_number)
    paginator = Paginator(exact_queryset, 24)
    page_obj = paginator.get_page(page_number)

    current_page = page_obj.number
    total_pages = paginator.num_pages

    start_page = max(current_page - 2, 1)
    end_page = min(current_page + 2, total_pages)

    page_range = range(start_page, end_page + 1)
    show_universal = request.GET.get('show_universal')
    context = {
        'products': page_obj,
        'suggested_products': suggested_products,
        'car_brands': CarBrand.objects.all(),
        'part_types': PartType.objects.all(),
        'search_query': search_query,
        'selected_brand': brand_id,
        'selected_part_type': part_type_id,
        'availability': availability,
        'order': order,
        'page_obj': page_obj,
        'page_range': page_range,
        'show_universal': show_universal,
    }

    return render(request, 'main/products.html', context)




def home(request):
    return render(request, 'main/home.html')

def product_detail(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    
    context = {
        'product': product,
    }
    return render(request, 'main/product.html', context)

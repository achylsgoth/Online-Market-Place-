from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
    }
    return render(request, 'store/home.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variants = product.variants.all()
    
    # Group variants by color and size for easier selection in template
    colors = set(v.color for v in variants if v.color)
    sizes = set(v.size for v in variants if v.size)
    
    context = {
        'product': product,
        'variants': variants,
        'colors': colors,
        'sizes': sizes,
    }
    return render(request, 'store/product_detail.html', context)

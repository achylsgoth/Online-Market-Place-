from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from store.models import Product, ProductVariant

def _get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_id)
    return cart

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        color_id = request.POST.get('color')
        size_id = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))
        
        # Find the specific variant
        variants = product.variants.all()
        if color_id:
            variants = variants.filter(color_id=color_id)
        if size_id:
            variants = variants.filter(size_id=size_id)
            
        if variants.exists():
            variant = variants.first()
        else:
            # Handle case where no specific variant matches (or product has no variants)
            # For now, if exact match fails, we might want to error or pick a default.
            # Assuming data is consistent, we should find a variant if options were presented.
            # If product has no variants, we might need a default variant or change logic.
            # For this simple implementation, let's assume a "default" variant exists if no options selected
            # or that the user MUST select options if they exist.
            # Let's try to find a variant with null color/size if not provided
            variant = product.variants.filter(color__isnull=not bool(color_id), size__isnull=not bool(size_id)).first()
            
        if not variant:
             # Fallback: create a dummy variant or handle error. 
             # For now, redirect back with error (not implemented) or just return.
             return redirect('product_detail', slug=product.slug)

        cart = _get_cart(request)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product_variant=variant)
        
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        
        return redirect('cart_detail')
    return redirect('home')

def cart_detail(request):
    cart = _get_cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

def remove_from_cart(request, item_id):
    cart = _get_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return redirect('cart_detail')

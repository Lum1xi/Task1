from django.http import JsonResponse
from django.shortcuts import render
from .main import parse_product
from products.models import Product
import json

# Create your views here.

def parse_view(request):
    """
    A view to trigger the selenium parser.
    Expects a 'url' query parameter, e.g., /selenium/parse/?url=https://example.com
    """
    url = request.GET.get('url')
    if not url:
        return JsonResponse({"error": "URL parameter is required"}, status=400, json_dumps_params={'ensure_ascii': False})

    # Call the parsing function
    data = parse_product(url)

    if data:
        Product.objects.create(**data)
        return JsonResponse({"message": "Successfully saved to Database", "data": data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({"error": "Failed to parse the product data."}, status=500, json_dumps_params={'ensure_ascii': False})

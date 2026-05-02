from django.http import JsonResponse
from django.shortcuts import render

from .main import parse_product, search_product_and_parse
from products.models import Product

# Create your views here.


def parse_view(request):
    url = request.GET.get('url')
    query = request.GET.get('query')

    if query:
        data = search_product_and_parse(query)
    elif url:
        data = parse_product(url)
    else:
        return JsonResponse({"error": "URL or query parameter is required"}, status=400, json_dumps_params={'ensure_ascii': False})

    if data:
        Product.objects.create(**data)
        return JsonResponse({"message": "Successfully saved to Database", "data": data}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({"error": "Failed to parse the product data."}, status=500, json_dumps_params={'ensure_ascii': False})

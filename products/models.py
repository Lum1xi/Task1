from django.db import models

class Product(models.Model):
    full_name = models.CharField(max_length=255, null=True, blank=True)
    price = models.CharField(max_length=50, null=True, blank=True)
    reviews_count = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    memory = models.CharField(max_length=100, null=True, blank=True)
    manufacturer = models.CharField(max_length=100, null=True, blank=True)
    product_code = models.CharField(max_length=100, null=True, blank=True)
    screen_diagonal = models.CharField(max_length=100, null=True, blank=True)
    display_resolution = models.CharField(max_length=100, null=True, blank=True)
    all_photos = models.JSONField(default=list, blank=True)
    all_product_details = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.full_name or "Unknown Product"

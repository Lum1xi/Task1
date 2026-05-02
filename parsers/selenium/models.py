from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=50)
    memory = models.CharField(max_length=50)
    manufacturer = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    promo_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    photos = models.JSONField()
    product_code = models.CharField(max_length=50)
    review_count = models.IntegerField()
    screen_diagonal = models.CharField(max_length=50)
    display_resolution = models.CharField(max_length=50)
    characteristics = models.JSONField()

    def __str__(self):
        return self.name


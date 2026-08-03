from django.db import models
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, blank=True, default='Primary')

    def __str__(self):
        return self.name

class Model(models.Model):
    CATEGORY_CHOICES = (
        ('Ganapati', 'Ganapati'),
        ('Gauri', 'Gauri'),
        ('Devi', 'Devi'),
    )
    sku = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    size = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='models/', blank=True, null=True)
    purchase_price = models.IntegerField(validators=[MinValueValidator(0)])
    selling_price = models.IntegerField(validators=[MinValueValidator(0)])
    raw_material_cost = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    available = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    low_stock_at = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    wholesale_sold = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    retail_sold = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.sku} - {self.name}"
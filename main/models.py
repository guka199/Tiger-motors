from django.db import models


class CarBrand(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Car Brand Name"
    )

    def __str__(self):
        return self.name


class PartType(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Part Type Name"
    )

    def __str__(self):
        return self.name


class Product(models.Model):

    product_id = models.CharField(
        max_length=50,
        unique=True,
        db_column='sku',
        verbose_name="Product ID"
    )

    secondary_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Secondary ID"
    )

    name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Product Name"
    )

    name_ge = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Product Name (Georgian)"
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Product Description"
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True
    )

    available = models.BooleanField(
        default=True,
        blank=True,
        null=True
    )

    car_brands = models.ManyToManyField(
        CarBrand,
        related_name='products',
        blank=True
    )

    part_types = models.ManyToManyField(
        PartType,
        related_name='products',
        blank=True
    )
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name if self.name else self.product_id



class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='products/')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"

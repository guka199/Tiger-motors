from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import CarBrand, PartType, Product, ProductImage
from django.db import transaction
import re
import decimal


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def extract_price(price_str):
    """Extract decimal price from string"""
    if not price_str:
        return None

    match = re.search(r'\d+\.?\d*', str(price_str).strip())
    if match:
        try:
            return decimal.Decimal(match.group())
        except:
            return None
    return None


def is_georgian(char):
    """Check if character is Georgian"""
    return '\u10a0' <= char <= '\u10ff'


def extract_name_until_georgian_end(description):
    """
    Keep everything from start.
    Once Georgian starts, continue until last Georgian letter.
    Stop when non-Georgian appears AFTER Georgian block.
    """
    if not description:
        return ""

    description = description.strip()

    result = ""
    georgian_started = False

    for char in description:
        if is_georgian(char):
            georgian_started = True
            result += char
        elif not georgian_started:
            result += char
        elif georgian_started and char == " ":
            result += char
        else:
            break

    return result.strip()


# ============================================================================
# PRODUCT IMPORT RESOURCE
# ============================================================================

class ProductResource(resources.ModelResource):

    class Meta:
        model = Product
        fields = (
            'product_id',
            'secondary_id',
            'name_ge',
            'description',
            'price',
            'available',
        )
        import_id_fields = ('product_id',)

    def before_import(self, dataset, **kwargs):
        # Assign headers to match your Excel structure
        dataset.headers = [
            'description',
            'product_id',
            'unit',
            'quantity',
            'price',
        ]

        # Cut dataset at first empty row
        clean_rows = []
        for row in dataset.dict:
            product_id = str(row.get('product_id', '') or '').strip()
            if not product_id or product_id.lower() == 'none':
                break
            clean_rows.append(row)
        
        dataset.dict = clean_rows

    def before_import_row(self, row, **kwargs):
        try:
            description_raw = str(row.get('description', '')).strip()
            product_id = str(row.get('product_id', '')).strip()
            quantity = row.get('quantity')
            price_str = row.get('price')

            # ✅ CLEAN NAME LOGIC
            clean_name = extract_name_until_georgian_end(description_raw)

            row['product_id'] = product_id
            row['name_ge'] = clean_name
            row['description'] = clean_name
            row['_raw_description'] = description_raw  # ← store raw for later
            row['secondary_id'] = ""

            # Availability
            try:
                qty = int(float(quantity)) if quantity else 0
                row['available'] = qty > 0
            except:
                row['available'] = False

            # Price
            if price_str:
                row['price'] = extract_price(price_str)

        except Exception as e:
            print(f"Row processing error: {e}")

        return row

    def after_import_row(self, row, row_result, **kwargs):
        try:
            if row_result.import_type in ('new', 'update', 'skip'):
                product_id = str(row.get('product_id', '')).strip()
                description = str(row.get('_raw_description') or row.get('description', '')).strip()
                all_brands = list(CarBrand.objects.all())

                def assign_brands(pid=product_id, desc=description, brands=all_brands):
                    try:
                        product = Product.objects.get(product_id=pid)
                        matched = [b for b in brands if b.name.lower() in desc.lower()]
                        if matched:
                            print(f"Product exists: {Product.objects.filter(product_id=pid).exists()}")
                            product.car_brands.add(*matched)
                            print(f"Assigned brands {[b.name for b in matched]} to {pid}")
                    except Exception as e:
                        print(f"Brand assignment error for {pid}: {type(e).__name__}: {e}")

                transaction.on_commit(assign_brands)

        except Exception as e:
            print(f"after_import_row error: {e}")


# ============================================================================
# ADMIN REGISTRATION
# ============================================================================

admin.site.register(CarBrand)
admin.site.register(PartType)




class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # shows 3 empty upload slots by default
    fields = ('image', 'is_main')

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ('product_id', 'secondary_id', 'name_ge', 'price', 'available')
    list_filter = ('available',)
    search_fields = ('product_id', 'name_ge')
    inlines = [ProductImageInline]
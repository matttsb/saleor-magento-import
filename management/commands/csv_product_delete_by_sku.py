import csv
from django.core.management import BaseCommand
import requests
import json
from saleor.product.models import Category, Collection, Product, ProductVariant, ProductImage
from django.conf import settings
from decimal import Decimal

# USAGE:
# python manage.py csv_product_delete_by_sku path/to/file.csv
# file.csv should contain one column named 'sku', all other columns ignored
# All SKUs will be deleted from saleor database


class Command(BaseCommand):
    help = 'Use to delete all products in a csv file by SKU.'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        input_file = csv.DictReader(open(options['file']))
        for magento_product in input_file:
            pv = ProductVariant.objects.filter(
                sku=magento_product['sku']).first()
            if pv:
                prod = pv.product_id
                ProductImage.objects.filter(product_id=prod).delete()
                ProductVariant.objects.filter(product_id=prod).delete()
                Product.objects.filter(pk=prod).delete()

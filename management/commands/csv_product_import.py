import csv

import requests
import json
from saleor.product.models import Category, Collection, Product, ProductVariant, ProductImage
from django.conf import settings
from decimal import Decimal
from django.core.management import BaseCommand

# USAGE:
# python manage.py csv_product_import path/to/file.csv
# file.csv should contain one column named 'sku', all other columns ignored
# You will need to copy your images from Magento into 'media/products' on your saleor installation
# Tested with CSV exported from magento 2.x
# - magentos simple product type only, all other product types ignored
# - currently only imports sku, name, description, price, and base image


def get_category_id(name):
    category_levels = name.split(',', 1)[0].split('/')
    parentid = 1
    level = 0
    for category in category_levels:
        if not Category.objects.filter(name=category):
            print("creating category " + category)
            if level > 0:
                newcat = Category.objects.create(name=category, parent=newcat)
            else:
                newcat = Category.objects.create(name=category)
            level += 1
            parentid = newcat.pk
        else:
            getcat = Category.objects.filter(name=category_levels[-1]).first()
            if getcat:
                parentid = getcat.id
    return parentid


class Command(BaseCommand):
    help = 'Import products'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        input_file = csv.DictReader(open(options['file']))
        for magento_product in input_file:
            check_exists = ProductVariant.objects.filter(
                sku=magento_product['sku'])
            if magento_product['product_type'] == 'simple' and not magento_product['custom_options']:
                if not check_exists:
                    print("creating : %s" % (magento_product['sku']))
                    imported_product = Product.objects.create(
                        name=magento_product['name'],
                        description=magento_product['description'],
                        price=magento_product['price'],
                        product_type_id=1,
                        category_id=get_category_id(
                            magento_product['categories']))

                    ProductVariant.objects.create(
                        sku=magento_product['sku'],
                        product=imported_product)
                    if magento_product['base_image']:
                        ProductImage.objects.create(
                            product=imported_product,
                            image='products' + magento_product['base_image']
                        )
                else:
                    print("updating : %s" % (magento_product['sku']))
                    saleor_productv = ProductVariant.objects.get(
                        sku=magento_product['sku'])
                    saleor_productv.categories = 'default'
                    saleor_productv.price = magento_product['price']
                    saleor_productv.name = magento_product['name']
                    saleor_productv.description = magento_product['description']
                    saleor_productv.save()
                    saleor_product = Product.objects.get(
                        pk=saleor_productv.product_id)
                    saleor_product.price = magento_product['price']
                    saleor_productv.save()
            else:
                print('Ignoring non simple product type or product with options')

import datetime
import json

from django.http import JsonResponse
from django.shortcuts import render

from .models import *
from .utils import cartData, cookieCart


def store(request):
    cart_data = cartData(request)
    items = cart_data["items"]
    order = cart_data["order"]
    cart_items_quantity = cart_data["cart_items_quantity"]
    products = Product.objects.all()
    context = {
        "products": products,
        "items": items,
        "order": order,
        "cart_items_quantity": cart_items_quantity,
        "shipping": False,
    }
    return render(request, "store/store.html", context)


def cart(request):
    cart = request.COOKIES["cart"]
    cart_data = cartData(request)
    items = cart_data["items"]
    order = cart_data["order"]
    cart_items_quantity = cart_data["cart_items_quantity"]

    context = {
        "items": items,
        "order": order,
        "cart_items_quantity": cart_items_quantity,
        "shipping": False,
    }
    return render(request, "store/cart.html", context)


def checkout(request):
    cart_data = cartData(request)
    items = cart_data["items"]
    order = cart_data["order"]
    cart_items_quantity = cart_data["cart_items_quantity"]
    context = {
        "items": items,
        "order": order,
        "cart_items_quantity": cart_items_quantity,
        "shipping": False,
    }
    return render(request, "store/checkout.html", context)


def update_item(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderitem, created = OrderItem.objects.get_or_create(product=product, order=order)

    if action == "add":
        orderitem.quantity = orderitem.quantity + 1
    elif action == "remove":
        orderitem.quantity = orderitem.quantity - 1

    orderitem.save()

    if orderitem.quantity <= 0:
        orderitem.delete()
    return JsonResponse("item was updated", safe=False)


def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()
    print("DATA:", request.body)
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        print("user is not logged_in")
        print("COOKIES:", request.COOKIES)

        name = data["form"]["name"]
        email = data["form"]["email"]

        cookie_data = cookieCart(request)
        items = cookie_data["items"]

        customer, created = Customer.objects.get_or_create(email=email)
        customer.name = name
        customer.save()

        order = Order.objects.create(
            customer=customer,
            complete=False,
        )

        for item in items:
            product = Product.objects.get(id=item["product"]["id"])
            order_item = OrderItem.objects.create(
                product=product,
                order=order,
                quantity=item["quantity"],
            )

    total = float(data["form"]["total"])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data["shipping"]["address"],
            city=data["shipping"]["city"],
            state=data["shipping"]["state"],
            zipcode=data["shipping"]["zipcode"],
        )

    return JsonResponse("Payment submitted..", safe=False)

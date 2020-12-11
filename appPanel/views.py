import json

import requests
from django.views.decorators.csrf import csrf_exempt

from .models import Restaurant, Menu, Food, Order
from . import response
from .serializers import MenuSerializer, RestaurantResponseSerializer, OrderSerializer


def token_validation(token):
    r = requests.post("http://localhost:8000/auth/verify", data={}, headers={"token": token})
    if r.status_code == 200:
        info = r.json()['data']
        return info
    else:
        raise Exception("Token is invalid")


def extract_request_data_post(request):
    try:
        if len(request.POST.keys()) > 0:
            request_data = request.POST
        else:
            request_data = json.load(request)
        return request_data
    except:
        return {}


def extract_request_headers(request):
    request_data = request.headers
    return request_data


def validate_required_body_items(required_fields, request_data):
    errors = []
    for item in required_fields:
        if item not in request_data.keys():
            errors.append(item + " is required!")

    return errors


def validate_required_header_items(required_fields, request_headers):
    errors = []
    for item in required_fields:
        if item not in request_headers.keys():
            errors.append(item + " is required!")

    return errors


def get_or_create_restaurant(username):
    try:
        restaurant = Restaurant.objects.get(username=username)
        return restaurant
    except Exception as e:
        if str(e) == "Restaurant matching query does not exist.":
            menu = Menu()
            menu.save()
            restaurant = Restaurant(username=username, menu=menu)
            restaurant.save()
            return restaurant
        else:
            raise e


@csrf_exempt
def get_restaurants_list(request):
    if request.method == 'GET':
        try:
            restaurants = Restaurant.objects.all()

            resp = []
            for rest in restaurants:
                resp.append(RestaurantResponseSerializer(rest).data)

            return response.success_response(resp)
        except:
            return response.internal_server_error_response()
    return response.method_not_allowed_response()


@csrf_exempt
def get_restaurant(request, username):
    if request.method == 'GET':
        try:
            restaurant = Restaurant.objects.get(username=username)
            return response.success_response(RestaurantResponseSerializer(restaurant).data)
        except Exception as e:
            if str(e) == "Restaurant matching query does not exist.":
                return response.not_found_response("Restaurant Not Found!")
            else:
                return response.internal_server_error_response()
    return response.method_not_allowed_response()


@csrf_exempt
def restaurant_menu(request, username):
    if request.method == "GET":
        try:
            restaurant = Restaurant.objects.get(username=username)
            return response.success_response(MenuSerializer(restaurant.menu).data)
        except Exception as e:
            if str(e) == "Restaurant matching query does not exist.":
                return response.not_found_response("Restaurant Not Found!")
            else:
                return response.internal_server_error_response()
    elif request.method == "POST":
        try:
            # Validate Header
            request_headers = extract_request_headers(request)
            required_headers_fields = ["token"]
            errors = validate_required_header_items(required_headers_fields, request_headers)
            if len(errors) > 0:
                return response.bad_request_response(errors)

            # Validate Body
            request_data = extract_request_data_post(request)
            required_data_fields = ["foods"]
            errors = validate_required_header_items(required_data_fields, request_data)
            if len(errors) > 0:
                return response.bad_request_response(errors)
            for food_data in request_data['foods']:
                required_data_fields = ['name', 'price', 'availability']
                errors = validate_required_header_items(required_data_fields, food_data)
                if len(errors) > 0:
                    return response.bad_request_response(errors)

            info = token_validation(request_headers["token"])
            if info['role'] != "RESTAURANT" or info['username'] != username:
                return response.forbidden_response()

            restaurant = get_or_create_restaurant(info["username"])
            for food_data in request_data['foods']:
                food = Food(name=food_data['name'], price=food_data['price'], availability=food_data['availability'])
                food.menu = restaurant.menu
                food.save()
            return response.success_response("OK")
        except Exception as e:
            if str(e) == "Token is invalid":
                return response.un_authorized_response()
            else:
                return response.internal_server_error_response()

    return response.method_not_allowed_response()


@csrf_exempt
def open_restaurant(request):
    if request.method == "PUT":
        try:
            # Validate Header
            request_headers = extract_request_headers(request)
            required_headers_fields = ["token"]
            errors = validate_required_header_items(required_headers_fields, request_headers)
            if len(errors) > 0:
                return response.bad_request_response(errors)

            info = token_validation(request_headers["token"])
            if info['role'] != "RESTAURANT":
                return response.forbidden_response()

            restaurant = Restaurant.objects.get(username=info['username'])
            restaurant.is_open = True
            restaurant.save()
            return response.success_response("OK")
        except Exception as e:
            if str(e) == "Token is invalid":
                return response.un_authorized_response()
            elif str(e) == "Restaurant matching query does not exist.":
                return response.bad_request_response("You must create menu")
            else:
                return response.internal_server_error_response()

    return response.method_not_allowed_response()


@csrf_exempt
def close_restaurant(request):
    if request.method == "PUT":
        try:
            # Validate Header
            request_headers = extract_request_headers(request)
            required_headers_fields = ["token"]
            errors = validate_required_header_items(required_headers_fields, request_headers)
            if len(errors) > 0:
                return response.bad_request_response(errors)

            info = token_validation(request_headers["token"])
            if info['role'] != "RESTAURANT":
                return response.forbidden_response()

            restaurant = Restaurant.objects.get(username=info['username'])
            restaurant.is_open = False
            restaurant.save()
            return response.success_response("OK")
        except Exception as e:
            if str(e) == "Token is invalid":
                return response.un_authorized_response()
            elif str(e) == "Restaurant matching query does not exist.":
                return response.bad_request_response("You must create menu")
            else:
                return response.internal_server_error_response()

    return response.method_not_allowed_response()


@csrf_exempt
def update_food(request, username, food_id):
    if request.method == "PUT":
        try:
            # Validate Header
            request_headers = extract_request_headers(request)
            required_headers_fields = ["token"]
            errors = validate_required_header_items(required_headers_fields, request_headers)
            if len(errors) > 0:
                return response.bad_request_response(errors)

            info = token_validation(request_headers["token"])
            if info['role'] != "RESTAURANT" or info['username'] != username:
                return response.forbidden_response()

            restaurant = Restaurant.objects.get(username=info['username'])
            # Validate Body
            request_data = extract_request_data_post(request)
            food = Food.objects.get(menu=restaurant.menu, id=food_id)
            if "name" in request_data.keys():
                food.name = request_data['name']
            if "price" in request_data.keys():
                food.price = request_data['price']
            if 'availability' in request_data.keys():
                food.availability = request_data['availability']
            food.save()
            return response.success_response("OK")
        except Exception as e:
            if str(e) == "Token is invalid":
                return response.un_authorized_response()
            elif str(e) == "Restaurant matching query does not exist.":
                return response.bad_request_response("You must create menu")
            else:
                return response.internal_server_error_response()

    return response.method_not_allowed_response()


@csrf_exempt
def order(request, username):
    if request.method == "GET":
        try:
            # Validate Header
            request_headers = extract_request_headers(request)
            required_headers_fields = ["token"]
            errors = validate_required_header_items(required_headers_fields, request_headers)
            if len(errors) > 0:
                return response.bad_request_response(errors)

            info = token_validation(request_headers["token"])
            if info['role'] != "RESTAURANT" or info['username'] != username:
                return response.forbidden_response()

            restaurant = Restaurant.objects.get(username=info['username'])
            orders = restaurant.orders
            order_list = []
            for order in orders.get_queryset():
                order_list.append(OrderSerializer(order).data)
            return response.success_response(order_list)
        except Exception as e:
            if str(e) == "Token is invalid":
                return response.un_authorized_response()
            if str(e) == "Order matching query does not exist.":
                return response.success_response([])
            elif str(e) == "Restaurant matching query does not exist.":
                return response.bad_request_response("You must create menu")
            else:
                return response.internal_server_error_response()
    elif request.method == "POST":
        try:
            request_headers = extract_request_headers(request)
            required_headers_fields = ["token"]
            errors = validate_required_header_items(required_headers_fields, request_headers)
            if len(errors) > 0:
                return response.bad_request_response(errors)

            info = token_validation(request_headers["token"])
            if info['role'] != "INTERNAL":
                return response.forbidden_response()
            request_data = extract_request_data_post(request)
            required_data_fields = ["foods", "customer"]
            errors = validate_required_header_items(required_data_fields, request_data)
            if len(errors) > 0:
                return response.bad_request_response(errors)
            restaurant = Restaurant.objects.get(username=username)
            if not restaurant.is_open:
                return response.bad_request_response("Restaurant is closed")
            order = Order(restaurant=restaurant, customer=request_data['customer'])
            foods_set = []
            total_price = 0
            for food in request_data['foods']:
                food_obj = Food.objects.get(id=food, menu=restaurant.menu)
                foods_set.append(food_obj)
                total_price = total_price + food_obj.price
            order.total_price = total_price
            order.save()
            order.foods.add(*foods_set)
            return response.success_response(OrderSerializer(order).data)
        except Exception as e:
            if str(e) == "Token is invalid":
                return response.un_authorized_response()
            elif str(e) == "Restaurant matching query does not exist.":
                return response.not_found_response("Restaurant not Found")
            elif str(e) == "Food matching query does not exist.":
                return response.not_found_response("Food not Found")
            else:
                return response.internal_server_error_response()
    return response.method_not_allowed_response()


@csrf_exempt
def get_order(request, username, order_id):
    if request.method == "GET":
        try:
            request_headers = extract_request_headers(request)
            required_headers_fields = ["token"]
            errors = validate_required_header_items(required_headers_fields, request_headers)
            if len(errors) > 0:
                return response.bad_request_response(errors)

            info = token_validation(request_headers["token"])
            if info['role'] != 'INTERNAL' and (info['role'] != "RESTAURANT" or info['username'] != username):
                return response.forbidden_response()
            restaurant = Restaurant.objects.get(username=username)
            order = Order.objects.get(restaurant=restaurant, id=order_id)
            return response.success_response(OrderSerializer(order).data)
        except Exception as e:
            if str(e) == "Order matching query does not exist.":
                return response.success_response([])
            elif str(e) == "Restaurant matching query does not exist.":
                return response.bad_request_response("You must create menu")
            else:
                return response.internal_server_error_response()
    return response.method_not_allowed_response()


@csrf_exempt
def deliver_order(request, username, order_id):
    if request.method == "PUT":
        try:
            request_headers = extract_request_headers(request)
            required_headers_fields = ["token"]
            errors = validate_required_header_items(required_headers_fields, request_headers)
            if len(errors) > 0:
                return response.bad_request_response(errors)

            info = token_validation(request_headers["token"])
            if info['role'] != "RESTAURANT" or info['username'] != username:
                return response.forbidden_response()
            restaurant = Restaurant.objects.get(username=username)
            order = Order.objects.get(restaurant=restaurant, id=order_id)
            order.status = True
            order.save()
            return response.success_response("OK")
        except Exception as e:
            if str(e) == "Token is invalid":
                return response.un_authorized_response()
            if str(e) == "Order matching query does not exist.":
                return response.success_response([])
            elif str(e) == "Restaurant matching query does not exist.":
                return response.bad_request_response("You must create menu")
            else:
                return response.internal_server_error_response()
    return response.method_not_allowed_response()

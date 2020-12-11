from django.urls import path
from . import views

urlpatterns = [
    path('/', views.get_restaurants_list, name='get restaurants'),
    path('/<str:username>', views.get_restaurant, name='get restaurants'),
    path('/<str:username>/menu', views.restaurant_menu, name='get restaurant menu'),
    path('/status/close', views.close_restaurant, name='close restaurant'),
    path('/status/open', views.open_restaurant, name='open restaurant'),
    path('/<str:username>/menu/foods/<int:food_id>', views.update_food, name='update food info'),
    path('/<str:username>/order', views.order, name='order'),
    path('/<str:username>/order/<int:order_id>', views.get_order, name='order'),
    path('/<str:username>/order/<int:order_id>/deliver', views.deliver_order, name='order')
]

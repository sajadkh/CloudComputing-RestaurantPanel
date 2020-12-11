from django.db import models


# Create your models here.

class Menu(models.Model):
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return self.id


class Food(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0)
    availability = models.IntegerField(default=0)
    menu = models.ForeignKey(Menu, related_name='foods', on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.id


class Restaurant(models.Model):
    id = models.AutoField(primary_key=True)
    menu = models.OneToOneField(
        Menu,
        on_delete=models.CASCADE,
        blank=True
    )
    is_open = models.BooleanField(default=False)
    username = models.CharField(max_length=32, blank=False)

    def __str__(self):
        return self.username


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    foods = models.ManyToManyField(Food, related_name='foods')
    total_price = models.FloatField(default=0.0, blank=False)
    status = models.BooleanField(default=False)
    restaurant = models.ForeignKey(Restaurant, related_name='orders', on_delete=models.CASCADE)
    customer = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return self.id

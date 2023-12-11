from django.db import models
from Adminapp.models import *
# Create your models here.

class Account_details(models.Model):
    type=[
        ('individual','individual'),
        ('company','company')
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    account_holder_name = models.CharField(max_length=1000,null=True,blank=True)
    account_number = models.CharField(max_length=1000,null=True,blank=True)
    account_holder_type=models.CharField(choices=type,max_length=2000,null=True)
    routing_number = models.CharField(max_length=2000,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

        
        
    

class FoodCategories(models.Model):
    Type=[
        ("Food","Food"),
        ("Drinks","Drinks")
    ]
    
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    category_image=models.ImageField(upload_to='category_image',null=True,blank=True)
    category_name=models.CharField(max_length=200,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    cat_type=models.CharField(choices=Type,max_length=100,null=True)
    status=models.CharField(max_length=100,null=True,default='live')
    updated_at=models.DateTimeField(auto_now=True)



class FoodName(models.Model):  
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    category_name=models.ForeignKey(FoodCategories,on_delete=models.CASCADE, related_name="cat", null=True)
    food_name=models.CharField(max_length=200,null=True,blank=True)
    food_image=models.ImageField(upload_to='food_image',null=True,blank=True)
    price=models.FloatField(null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    discount=models.FloatField(default=0)
    discountPrice=models.FloatField(default=0)
    updated_at=models.DateTimeField(auto_now=True)
    status=models.CharField(max_length=100,null=True)
    is_active=models.BooleanField(default=1)
    text_color_type=models.CharField(max_length=100,null=True,blank=True)
    background_color_type=models.CharField(max_length=100,null=True,blank=True)

class foodincludes(models.Model):
    name=models.CharField(max_length=5000,null=True,blank=True)
    food_name=models.ForeignKey(FoodName,on_delete=models.CASCADE,null=True,related_name='included')
    status=models.BooleanField(default=True)


class FoodLevel(models.Model):
    food=[
        ('Mild','Mild'),
        ('Medium','Medium'),
        ('Hot','Hot'),
    ]
    drinks=[
        ('Cold','Cold'),
        ('Moderate','Moderate'),
        ('Hot','Hot'),
    ]
    food_name=models.ForeignKey(FoodName,on_delete=models.CASCADE,null=True,related_name='level')
    drinks_level=models.CharField(null=True,choices=drinks,max_length=1000)
    food_level=models.CharField(null=True,choices=food,max_length=1000)




class Extra(models.Model):
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    food_name=models.ForeignKey(FoodName,on_delete=models.CASCADE,null=True)

class Top_Choices(models.Model):
    top_choices=[
        ("#1 favorite","#1 favorite"),
        ("#2 favorite","#2 favorite"),
        ("#3 favorite","#3 favorite"),
    ]
    top_choice=models.CharField(null=True,choices=top_choices,max_length=1000)
    foodname=models.ForeignKey(FoodName, on_delete=models.CASCADE,null=True,blank=True)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
   
class Addons_Group(models.Model):
    choice_instruction=[
        ("select only one (1)","select only one (1)"),
        ("select more than one (1)","select more than one (1)"),
    ]
    group_name=models.CharField(max_length=200,null=True,blank=True)
    foodname=models.ForeignKey(FoodName, on_delete=models.CASCADE,null=True,blank=True,related_name='addon')
    status=models.BooleanField(default=1)
    group_type=models.CharField(max_length=200,default='Optional')
    instruction=models.CharField(choices=choice_instruction,null=True,max_length=200)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)

class AddOnes(models.Model):
    group_name=models.ForeignKey(Addons_Group, on_delete=models.CASCADE,null=True,blank=True,related_name='group')
    name=models.CharField(max_length=200,null=True,blank=True)
    price=models.FloatField(null=True,blank=True,default=0)
    status=models.BooleanField(default=1)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    def save(self, *args, **kwargs):
        # Round the price to two decimal places before saving
        self.price = round(self.price, 2)
        super(AddOnes, self).save(*args, **kwargs)

    
class Addtocart(models.Model):
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    food_id=models.ForeignKey(FoodName, on_delete=models.CASCADE,null=True,blank=True)
    unique_id=models.CharField(max_length=2000,null=True,blank=True)
    spicelevel=models.CharField(max_length=2000,null=True,blank=True)
    quantity = models.IntegerField(null=True,blank=True,default=1)
    price = models.FloatField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    food_instruction=models.CharField(max_length=2000,null=True,blank=True)

class Order(models.Model):
    CHOICES=[
        ('Pending','Pending'),
        ('Order_sent','Order_sent')
    ]
    order_id=models.IntegerField(default=0)
    status=models.CharField(choices=CHOICES,null=True,blank=True,max_length=200 ,default='Pending')
    created_at=models.DateTimeField(auto_now_add=True)
    order_sent_date=models.DateTimeField(auto_now=True,null=True,blank=True)
    totalprice=models.FloatField(null=True)
    quantity = models.IntegerField(null=True,blank=True)
    table_number=models.IntegerField(null=True,blank=True)
    tip_amount=models.FloatField(null=True)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    newrating=models.IntegerField(null=True,blank=True)
    review=models.CharField(max_length=500,null=True,blank=True)
    order_type=models.CharField(max_length=200,null=True,blank=True)
    item_instruction=models.BooleanField(default=False)
    restaurnt_payment_status=models.CharField(max_length=100,null=True)
    customer_distance_range=models.CharField(max_length=100,null=True)
    
class User_unique_id(models.Model):
    unique_id=models.CharField(max_length=1000,null=True)
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    order_type=models.CharField(max_length=200,null=True,blank=True)
    latitude=models.FloatField(null=True,blank=True)
    longitude=models.FloatField(null=True,blank=True)

class UserDetails(models.Model):
    name=models.CharField(max_length=200,null=True,blank=True)
    email_id=models.EmailField(null=True)
    phone_number=models.BigIntegerField(null=True)
    unique_id=models.CharField(max_length=2000,null=True,blank=True)
    order_id=models.ForeignKey(Order, on_delete=models.CASCADE,null=True,blank=True, related_name='alluser')
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    total_price=models.FloatField(null=True)
    tip_amount=models.FloatField(null=True)
    table_number=models.IntegerField(null=True,blank=True)
    payment_statud=models.BooleanField(default=0)
    restaurnt_payment_status=models.CharField(max_length=100,null=True)
    customer_distance_range=models.CharField(max_length=100,null=True)
    
class Allorders(models.Model):
    order_id=models.ForeignKey(Order,on_delete=models.CASCADE, null=True,blank=True , related_name='allorders')
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    food_id=models.ForeignKey(FoodName,on_delete=models.CASCADE,null=True,blank=True)
    food_name=models.CharField(max_length=200,null=True,blank=True)
    food_image=models.ImageField(upload_to='food_image',null=True,blank=True)
    food_price=models.FloatField(null=True,blank=True)
    quantity = models.IntegerField(null=True,blank=True)
    spicelevel=models.CharField(max_length=2000,null=True,blank=True)
    price=models.DecimalField(decimal_places=3, max_digits=64 , null=True)
    food_instruction=models.CharField(max_length=2000,null=True,blank=True)
    
class FoodAddonce(models.Model):
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    food_id=models.ForeignKey(FoodName, on_delete=models.CASCADE,null=True,blank=True)
    addonce_id=models.ForeignKey(AddOnes, on_delete=models.CASCADE,null=True,blank=True)
    order_id=models.ForeignKey(Allorders, on_delete=models.CASCADE,null=True,blank=True)
    addtocart=models.ForeignKey(Addtocart, on_delete=models.CASCADE,null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    unique_id=models.CharField(max_length=2000,null=True,blank=True)

class FoodIncludes_add(models.Model):
    addtocart=models.ForeignKey(Addtocart, on_delete=models.CASCADE,null=True,blank=True)
    name=models.CharField(max_length=5000,null=True,blank=True)

class FoodAdd(models.Model):
    order_id=models.ForeignKey(Allorders,on_delete=models.CASCADE,null=True ,related_name='abc')
    addonce_id=models.ForeignKey(AddOnes,on_delete=models.CASCADE,null=True,blank=True)

class Selected_FoodIncludes_add(models.Model):
    order_id=models.ForeignKey(Allorders,on_delete=models.CASCADE,null=True ,related_name='abcd')
    name=models.CharField(max_length=5000,null=True,blank=True)

class OrderPayment(models.Model):
    order_id=models.ForeignKey(Order,on_delete=models.CASCADE,null=True ,related_name='abcd')
    user=models.ForeignKey(UserDetails,on_delete=models.CASCADE,null=True ,related_name='user')
    status=models.CharField(max_length=100,blank=True,null=True)
    users_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    order_transfer_date=models.DateField(null=True)


class Transfer_amount_details(models.Model):
    users_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    account_id=models.ForeignKey(Account_id,on_delete=models.CASCADE,null=True)
    transfer_id=models.CharField(max_length=1000,null=True,blank=True)
    amount=models.FloatField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
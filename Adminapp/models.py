from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.
class CustomuserManager(BaseUserManager):
    def create_user(self ,full_name , email_id , password ,restaurant_name, phone_number=None,restaurant_logo=None,restaurant_address=None ,country=None ,Postal_code=None,state=None,city=None):
       
        if not email_id:
            raise ValueError("The Email must be set")
        user = self.model(
            email_id=self.normalize_email(email_id),
            full_name=full_name,
            phone_number=phone_number,
            restaurant_name=restaurant_name,
            restaurant_logo=restaurant_logo,
            restaurant_address=restaurant_address,
            country=country,
            state=state,
            city=city,
            Postal_code=Postal_code,

        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    

    def create_superuser(self , full_name , email_id , password , phone_number  ):
        """
        Creates and saves a superuser with the given email, name, tc and password.
        """
        user = self.create_user(
            full_name=full_name,
            email_id=email_id,
            phone_number=phone_number,
            password=password,
            restaurant_name=None,
            restaurant_logo=None,
            restaurant_address=None,
            country=None,
            Postal_code=None,
        )
        
        user.is_superuser = True
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user
    
class CustomUser(AbstractBaseUser):
    email_id = models.EmailField(verbose_name='email_id', max_length=255, unique=True, null=True)
    username=models.CharField(max_length=1000,null=True,blank=True)
    full_name=models.CharField(max_length=1000,null=True,blank=True)
    phone_number = models.CharField(max_length=10,null=True,blank=True)
    country = models.CharField(max_length=1000,null=True,blank=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default = True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    is_superuser = models.BooleanField(default=False)
    Postal_code = models.IntegerField(null=True,blank=True)
    restaurant_name=models.CharField(max_length=1000,null=True,blank=True)
    restaurant_logo=models.FileField(upload_to='restaurant_logo' ,blank=True)
    banner_image=models.FileField(upload_to='banner_image' ,blank=True)
    restaurant_address=models.CharField(max_length=3000,null=True,blank=True)
    city=models.CharField(max_length=3000,null=True,blank=True)
    state=models.CharField(max_length=3000,null=True,blank=True)
    qr_code=models.ImageField(upload_to='qr_code',blank=True)
    payment_status=models.CharField(max_length=200,default='pending')
    payment_price=models.CharField(max_length=200,default='0')
    package=models.CharField(max_length=200,default='pending')
    open_time=models.CharField(max_length=100,null=True,blank=True)
    close_time=models.CharField(max_length=100,null=True,blank=True)
    subscription_date=models.CharField(null=True,blank=True,max_length=100)
    subscritpion_expire_date=models.CharField(null=True,blank=True,max_length=100)
    payment_diable_enable_status=models.CharField(max_length=200 ,default=False)
    currency=models.CharField(max_length=200 ,null=True,blank=True)
    table_number_status=models.BooleanField(default=0)
    count1=models.IntegerField(default=0)
    service_fee=models.FloatField(default=0)
    
    def __str__(self):
        return f'{self.email} - {self.id}'


    def save(self,*args,**kwargs):
        if self.email_id:
            self.email_id = self.email_id.lower()  # Convert email to lowercase
        super(CustomUser, self).save(*args, **kwargs)
        

    objects = CustomuserManager()

    USERNAME_FIELD = 'email_id'
    EMAIL_FIELD = 'email_id'
    REQUIRED_FIELDS = ['full_name','phone_number',]

    def __str__(self):
        return self.email_id
    

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

class Restaurnt_type(models.Model):
    type=[
        ('Restaurant','Restaurant'),
        ('Food Truck','Food Truck')
    ]
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    restaurant_type=models.CharField(choices=type,null=True,max_length=200)

class Account_id(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    account_id=models.CharField(max_length=2000,null=True,blank=True)
    bank_id = models.CharField(max_length=2000,null=True,blank=True)
    status=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)


class SubscriptionDetails(models.Model):
    monthly_price=models.FloatField(null=True,blank=True)
    yearly_price=models.FloatField(null=True,blank=True)
    # status=models.BooleanField(default=0)

class subscription_features(models.Model):
    points=models.CharField(max_length=500,null=True,blank=True)
    subscription=models.ForeignKey(SubscriptionDetails,on_delete=models.CASCADE,null=True)


class Notification(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True,blank=True)
    sender = models.CharField(max_length=200,null=True,blank=True)
    receiver = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True,related_name='reciver_user')
    read=models.BooleanField(default=False)
    status=models.CharField(max_length=100,default='live')
    order_id=models.IntegerField(null=True,blank=True)
    
    


class Termandcondition(models.Model):
    img=models.ImageField(null=True,blank=True,upload_to='condition')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = RichTextUploadingField(max_length=100,null=True,blank=True)



class PrivacyAndPolicy(models.Model):
    img=models.ImageField(null=True,blank=True,upload_to='condition')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True,blank=True)


class CategoryImages(models.Model):
    image=models.ImageField(null=True,blank=True,upload_to='condition')
    user_id=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Food_Item_Suggestion(models.Model):
    food_name=models.CharField(max_length=3000,null=True,blank=True)
    food_type=models.CharField(max_length=3000,null=True,blank=True)
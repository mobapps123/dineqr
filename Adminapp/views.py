from django.shortcuts import render,redirect,HttpResponse 
from .models import *
from django.views import View
from django.contrib.auth import authenticate, login as dj_login, logout
from django.contrib import messages
from restaurantadminapp.models import *
from django.http import JsonResponse
from io import BytesIO
from PIL import Image, ImageDraw
import qrcode                                                                  
from django.urls import reverse
from django.core.files import File
from cities_light.models import *
from countryinfo import CountryInfo
from babel.numbers import get_currency_symbol


class AdminDashboard(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.is_superuser is True:
                total_user=CustomUser.objects.all().filter(is_superuser=False).count()
                active=CustomUser.objects.all().filter(is_superuser=False,is_active=True).count()
                in_active=CustomUser.objects.all().filter(is_superuser=False,is_active=False).count()
                subs=CustomUser.objects.filter(payment_status='Successfull',is_superuser=False).count()
                return render(request,'admin/dashboard.html',{'total_user':total_user,'active':active,'in_active':in_active,'subs':subs})
            else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
        else:
            return redirect('admin-login')
        

def login(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            email_id = request.POST.get('email_id')
            passwords = request.POST.get('password')
            user = authenticate(request=request, email_id=email_id, password=passwords)
            if user is not None:
                if CustomUser.objects.filter(email_id=email_id, is_superuser=True):
                    dj_login(request, user)
                    return redirect('admin-dashboard')
                else:
                    messages.warning(request, 'You Are Not Admin User')
            else:
                messages.warning(request, 'Invalid Email or Password')
        return render(request, 'admin/login.html')
    else:
        return redirect('admin-dashboard')


def Admin_logout(request):
    logout(request)
    messages.success(request, 'Admin Logged Out Successfully..!!')
    return redirect('admin-login')




class Change_password(View):
    
    def get(self, request):
        if  request.user.is_authenticated:
            if request.user.is_superuser is True:
                return render(request, 'admin/password_reset.html')
            else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
        else:
            return redirect('admin-login') 
    def post(self, request):
        id=request.user.id
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        new_password = confirm_password
        user = CustomUser.objects.get(id=id)
        check=user.check_password(old_password)
    
        if check==True:
            user.set_password(new_password)
            user.save()
            
            messages.success(request, 'New password  Successfully..!!')
            return redirect("admin-dashboard")
        else:

            messages.error(request, '**Incorrect Old Password..!!')

        
        return redirect('change-password')



class ForgotPassword(View):
    def get(self,request):
        if not request.user.is_authenticated:
            return render(request,'admin/forget.html')
        else:
            return redirect('admin-dashboard')
    def post(self,request):
        email_id=request.POST.get('email_id')
        new_password=request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        if CustomUser.objects.filter(email_id=email_id,is_superuser=True).exists():
            user=CustomUser.objects.get(email_id=email_id)
            if new_password==confirm_password:
                user.set_password(new_password)
                user.save()
            
                messages.success(request, 'New password  Successfully..!!')
                return redirect("admin-login")
            else:
                messages.error(request,"New password and Confirm password should be same!")
                return redirect('forgot-password')
        else:
            messages.warning(request,"Email id doesnot exist.")
            return redirect('forgot-password')

    


#########################Show users ###############

class Add_Users(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.is_superuser is True:
                country=Country.objects.all()

                return render(request,'admin/users/add_users.html',{'country':country,'model':Restaurnt_type})
            else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
        else:
            return redirect('admin-login')
    def post(self,request): 
        restaurant_name=request.POST.get('restaurant_name')
        restaurant_logo=request.FILES.get('restaurant_logo')
        full_name=request.FILES.get('full_name')
        email_id=request.POST.get('email_id')
        phone_number=request.POST.get('phone_number')
        restaurant_address=request.POST.get('restaurant_address')
        password=request.POST.get('password') 
        country=request.POST.get('country') 
        state=request.POST.get('state') 
        city=request.POST.get('city') 
        restaurnt_type=request.POST.get('restaurant_type')
        
        userdata=CustomUser.objects.create_user(email_id=email_id,phone_number=phone_number,password=password,restaurant_name=restaurant_name,restaurant_address=restaurant_address,restaurant_logo=restaurant_logo,full_name=full_name,country=Country.objects.get(id=country).name,state=Region.objects.get(id=state).name,city=City.objects.get(id=city).name)

        Restaurnt_type.objects.create(user=userdata,restaurnt_type=restaurnt_type)

        #For Creating Qrcode
        url =request.build_absolute_uri(reverse('mobile_home', args=[str(userdata.id)]))
        qr_code_image = qrcode.make(url, version=None, error_correction=qrcode.constants.ERROR_CORRECT_H)
        new_size = max(qr_code_image.size) + 40
        canvas = Image.new('RGB', (new_size, new_size), 'white')
        draw = ImageDraw.Draw(canvas)
        qr_code_position = ((new_size - qr_code_image.size[0]) // 2, (new_size - qr_code_image.size[1]) // 2)
        canvas.paste(qr_code_image, qr_code_position)
        fname = f'qu_code-{userdata.restaurant_name}.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        userdata.qr_code.save(fname, File(buffer), save=False)
        canvas.close()
        userdata.save()
        return redirect('show-users')

class Show_Users(View):
    def get(self,request):
        if  request.user.is_authenticated:
            if request.user.is_superuser is True:
                users = CustomUser.objects.filter(is_superuser=False).all()
                return render(request,'admin/users/show_users.html',{'Users':users})
            else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
        else:
            return redirect('admin-login')



class Edit_Users(View):
    def get(self, request, id):
        if  request.user.is_authenticated:
            if request.user.is_superuser is True:
                data=CustomUser.objects.get(id=id)
                typee=Restaurnt_type.objects.get(user=data)
                print(typee.restaurant_type)
                country=Country.objects.all().exclude(name=data.country)
                if data.country:
                    country_add=Country.objects.get(name=data.country)
                else:
                    country_add=None
                all_state=Region.objects.filter(country_id=country_add).exclude(name=data.state)
                if data.state:
                    state=Region.objects.get(name=data.state,country_id=country_add.id)
                else:
                    state=None
                all_city=City.objects.filter(region_id=state).exclude(name=data.city)
                if data.city:
                    city=City.objects.get(name=data.city,region_id=state.id)
                else:
                    city=0
                return render(request, 'admin/users/edit_users.html', {'datas': data,'country':country,'country_add':country_add,'state':state,'all_state':all_state,'city':city,'all_city':all_city,'model':Restaurnt_type,'typee':typee})
            else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
        else:
            return redirect('admin-login')
    def post(self, request, id):
        rname=request.POST.get('restaurant_name')
        rlogo=request.FILES.get('restaurant_logo')
        country=request.POST.get('country')
        code=request.POST.get('code')
        email=request.POST.get('email')
        city=request.POST.get('city')
        state=request.POST.get('state')
        banner_image=request.FILES.get('banner_image')
        address=request.POST.get('restaurant_address')
        phone_number=request.POST.get('phone_number')
        email=request.POST.get('email_id')
        close_time=request.POST.get('close_time')
        open_time=request.POST.get('open_time')
        restuarant_type= request.POST.get('restuarant_type')
        print(restuarant_type)
        data=CustomUser.objects.get(id=id)
        typee=Restaurnt_type.objects.get(user=data)
        typee.restaurant_type=restuarant_type
        typee.save()


        url =request.build_absolute_uri(reverse('mobile_home', args=[str(data.id)]))
        qr_code_image = qrcode.make(url, version=None, error_correction=qrcode.constants.ERROR_CORRECT_H)
        new_size = max(qr_code_image.size) + 40
        canvas = Image.new('RGB', (new_size, new_size), 'white')
        draw = ImageDraw.Draw(canvas)
        qr_code_position = ((new_size - qr_code_image.size[0]) // 2, (new_size - qr_code_image.size[1]) // 2)
        canvas.paste(qr_code_image, qr_code_position)
        fname = f'qu_code-{data.restaurant_name}.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        data.qr_code.save(fname, File(buffer), save=False)
        canvas.close()
        if country:
            country12 = Country.objects.get(id=country).name
            try:
                currencies = CountryInfo(country12).currencies()
                data.currency=currencies[0]
                currency_code = currencies[0]
                currency_symbol = get_currency_symbol(currency_code, locale="en_US")
                data.currency=currency_symbol
            except KeyError:
                data.currency='$'
        if banner_image:
            data.banner_image = banner_image
        if rlogo:
            data.restaurant_logo=rlogo
        if country:
            data.country=Country.objects.get(id=country).name
        if code:
            data.Postal_code=code
        if city:
            data.city=City.objects.get(id=city).name
        if state:
            data.state=Region.objects.get(id=state).name
        else:
            data.state=None
            data.city=None
        data.email_id=email
        data.restaurant_name=rname
        data.restaurant_address=address
        data.phone_number=phone_number
        data.open_time=open_time
        data.close_time=close_time
        data.save()
        messages.success(request,'Profile Updated.')
        return redirect('edit-users', id)

# for user in CustomUser.objects.filter(is_superuser=False):
#     print(user.email_id)
#     data=Restaurnt_type.objects.create(user=user,restaurant_type = 'Restaurant')

# Restaurnt_type.objects.all().delete()

def Delete_Users(request ,id):
        if request.method=='POST':
            if request.user.is_superuser is True:
                pi=CustomUser.objects.get(pk=id)
                pi.delete()
        return redirect('show-users')


def Show_Profile(request,id):
    if  request.user.is_authenticated:
        if request.user.is_superuser is True:
            data = CustomUser.objects.get(id=id)
            return render(request, 'admin/users/profile.html', {'datas': data})
        else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
    else:
        return redirect('admin-login')


class Active_inActive(View):

    def post(self, request):
        user_id = request.POST.get('id')
        user = CustomUser.objects.get(id=user_id)
        if user.is_active is False:
            user.is_active = True
        elif user.is_active is True:
            user.is_active = False
        user.save()
        return redirect('show-users')
        
class Edit_Admin(View):
    def get(self, request):
        if  request.user.is_authenticated:
            if request.user.is_superuser is True:
                data = CustomUser.objects.get(id=request.user.id)
                return render(request, 'admin/users/edit_admin.html', {'datas': data})
            else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
        else:
            return redirect('admin-login')
    def post(self, request):
        full_name=request.POST.get('full_name')
        restaurant_logo=request.FILES.get('restaurant_logo')
        phone_number=request.POST.get('phone_number')
        email_id=request.POST.get('email_id')
        service_fee=request.POST.get('service_fee')
        data=CustomUser.objects.get(id=request.user.id)
        if restaurant_logo:
            data.restaurant_logo=restaurant_logo
        data.full_name=full_name
        data.phone_number=phone_number
        data.email_id=email_id
        data.save()
        CustomUser.objects.all().update(service_fee=service_fee)
        messages.success(request,'Update Succesfully!!!')
        return redirect('edit-admin')

class Payment_enable_diable(View):
    def post(self,request):
        data=Account_id.objects.get(user=request.user)
        if data.is_active == False:
            data.is_active=True
            data.save()
        else:
            data.is_active =False
            data.save()
        return JsonResponse({'msg':'Chnaged'})
    


class User_Payment(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.is_superuser is True:
                data=CustomUser.objects.filter(is_admin=False).order_by('restaurant_name')
                return render(request,'admin/payment.html',{'data':data})
            else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
        else:
            return redirect('admin-login')


class Show_SubscriptionsDetails(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.is_superuser is True:
                data=SubscriptionDetails.objects.all()
                return render(request,'admin/subscription_details/show_subscription_details.html',{'data':data})
            else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
        else:
            return redirect('admin-login')
        

class Edit_SubscriptionsDetails(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            if request.user.is_superuser is True:
                data=SubscriptionDetails.objects.get(id=id)
                return render(request,'admin/subscription_details/update_subscription_details.html',{'data':data})
            else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
        else:
            return redirect('admin-login')
    def post(self,request,id):
        subscription=SubscriptionDetails.objects.get(id=id)
        monthly_price=request.POST.get('monthly_price')
        yearly_price=request.POST.get('yearly_price')
        subscription.monthly_price=monthly_price
        subscription.yearly_price=yearly_price
        subscription.save()
        return redirect('show-subscription')

class Add_SubscriptionsDetails(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.is_superuser is True:
                return render(request,'admin/subscription_details/add_subscription_details.html')
            else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
        else:
            return redirect('admin-login')
    def post(self,request):
        subscription=SubscriptionDetails()
        monthly_price=request.POST.get('monthly_price')
        yearly_price=request.POST.get('yearly_price')
        subscription.monthly_price=monthly_price
        subscription.yearly_price=yearly_price
        subscription.save()
        return redirect('show-subscription')

class Add_subscription_features(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            return render(request,'admin/subscription_feature/add_subscription_feature.html')
        else:
            return redirect('admin-login')
    def post(self,request,id):
        features=subscription_features()
        points=request.POST.get('feature')
        features.points=points
        features.subscription=SubscriptionDetails.objects.get(id=id)
        features.save()
        return redirect('show_subscription_feature',id)
    
class Show_subscription_features(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            feature=subscription_features.objects.filter(subscription=SubscriptionDetails.objects.get(id=id))
            return render(request,'admin/subscription_feature/show_subscription_feature.html',{'feature':feature,'subs_id':id})
        else:
            return redirect('admin-login')


class Edit_subscription_features(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            feature=subscription_features.objects.get(id=id)
            return render(request,'admin/subscription_feature/edit_subscription_feature.html',{'feature':feature})
        else:
            return redirect('admin-login')
    def post(self,request,id):
        features=subscription_features.objects.get(id=id)
        points=request.POST.get('feature')
        features.points=points
        features.save()
        return redirect('show_subscription_feature',features.subscription.id)

class Delete_Subscription_feature(View):
    def post(self,request,id):
        data=subscription_features.objects.get(id=id)
        data.delete()
        return redirect('show_subscription_feature',data.subscription.id)

# def delete_subscriptionsdetails(request,id):
#     if request.user.is_superuser is True:
#         if request.method=='POST':
#             data=SubscriptionDetails.objects.get(id=id)
#             data.delete()
#         return redirect('show-subscription')
#     else:
#             messages.error(request,'You are not admin')
#             return redirect('user-login')
            
        
class enable_diable_subscription(View):
    def post(self,request):
        idd=request.POST.get('id')
        data=SubscriptionDetails.objects.get(id=idd)
        if data.status== 0 :
            data.status=1
            data.save()
        else:
            data.status=0
            data.save()
        return JsonResponse({'msg':"Changed"})
    
class menu_enable_diable_subscription(View):
    def post(self,request):
        idd=request.POST.get('id')
        data=SubscriptionDetails.objects.get(id=idd)
        if data.status== 0 :
            data.status=1
            data.save()
        else:
            data.status=0
            data.save()
        return JsonResponse({'msg':"Changed"})


        




def handler404(request, exception):
    return render(request, 'admin/page404.html', status=404)




class Add_Notifiactions(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.is_superuser is True:
                data=CustomUser.objects.all().filter(is_superuser=False)
                return render(request,'admin/add_notifications.html',{'datas':data})
            else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
            
        else:
                return redirect('admin-login')
    def post(self,request):
        description=request.POST.get('description')
        receiver = request.POST.getlist("receiver")
        
        
        try:
            if receiver ==['']:
                data=CustomUser.objects.all().filter(is_superuser=False)
                for data in data:
                    Notification.objects.create(description=description,receiver=data,sender=request.user)
                return redirect('show-notification')

            else:   
                for receiver in receiver:
                    
                    receiveruser=CustomUser.objects.get(id=int(receiver))
                    Notification.objects.create(description=description,receiver=receiveruser,sender=request.user.full_name )
                return redirect('show-notification')
        except ValueError:
            messages.error(request,'Select either allusers or only users')
            return redirect('sent-notification')
class Notifiactions_show(View):
    def get(self,request):
        if request.user.is_superuser is True:    
            users = Notification.objects.all()

            return render(request,'admin/show_notification.html',{'Users':users})
        else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
        

def delete_notifications(request,id):
        if request.user.is_superuser is True:
            if request.method=='POST':    
                users = Notification.objects.get(id=id)
                users.delete()

            return redirect('show-notification')
            
        else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
        
def delete_all_notifications(request):
        if request.user.is_superuser is True:   
            if request.method=='POST': 
                users = Notification.objects.all()
                users.delete()

            return redirect('show-notification')
        else:
                messages.error(request,'You are not admin')
                return redirect('user-login')
        

class Termsandconditions_add(View):
    def get(self,request):
        if  request.user.is_authenticated:
            return render(request,'admin/termandcondition/termandcom_add.html')
        else:
            return redirect('admin-login')
        
    def post(self,request):
        description=request.POST.get('description')
        img=request.FILES.get('img')

        Termandcondition.objects.create(img=img,description=description)
        return redirect('show-termandcondition')

class Termsandconditions_show(View):
    def get(self,request):
        if  request.user.is_authenticated:
            users = Termandcondition.objects.all().order_by('-id')
            return render(request,'admin/termandcondition/termandcon_view.html',{'Users':users})
        else:
            return redirect('admin-login')


class Termsandconditions_Edit(View):
    def get(self, request, id):
        if  request.user.is_authenticated:
            data = Termandcondition.objects.get(pk=id)
        
            
            return render(request, 'admin/termandcondition/termandcon_edit.html', {'datas': data})
        else:
            return redirect('admin-login')
        


    def post(self, request, id):
        data = Termandcondition()
        img=request.FILES.get('img')
        description=request.POST.get('description')
        data = Termandcondition.objects.get(id=id)
        if img is not None:
            Termandcondition(id=id,description=description, img=img,created_at=data.created_at).save()
        else:
            Termandcondition(id=id,description=description, img=data.img,created_at=data.created_at).save()

        return redirect('show-termandcondition')


def delete_Termsandconditions(request ,id):
        if request.method=='POST':
            pi=Termandcondition.objects.get(pk=id)
            pi.delete()
        return redirect('show-termandcondition')




class Privacyandpolicy_add(View):
    def get(self,request):
        if  request.user.is_authenticated:
            return render(request,'admin/privcayandpolicy/privacyandpolicy_add.html')
        else:
            return redirect('admin-login')
        
    def post(self,request):
        img=request.FILES.get('img')
        description=request.POST.get('description')

        PrivacyAndPolicy.objects.create(img=img,description=description)
        return redirect('show-privacyandpolicy')

class Privacyandpolicy_show(View):
    def get(self,request):
        if  request.user.is_authenticated:
            users = PrivacyAndPolicy.objects.all().order_by('-id')
            return render(request,'admin/privcayandpolicy/privacyandpolicy_view.html',{'Users':users})
        else:
            return redirect('admin-login')


class Privacyandpolicy_Edit(View):
    def get(self, request, id):
        if  request.user.is_authenticated:
            data = PrivacyAndPolicy.objects.get(pk=id)
            
            return render(request, 'admin/privcayandpolicy/privacyandpolicy_edit.html', {'datas': data})
        else:
            return redirect('admin-login')
        


    def post(self, request, id):
        data = PrivacyAndPolicy()
        img=request.FILES.get('img')

        description=request.POST.get('description')
        data = PrivacyAndPolicy.objects.get(id=id)
        if img is not None:
            PrivacyAndPolicy(id=id,img=img,description=description, created_at=data.created_at).save()
        else:
            PrivacyAndPolicy(id=id,img=data.img,description=description, created_at=data.created_at).save()

        return redirect('show-privacyandpolicy')


def delete_Privacyandpolicy(request ,id):
        if request.method=='POST':
            pi=PrivacyAndPolicy.objects.get(pk=id)
            pi.delete()
        return redirect('show-privacyandpolicy')



class Show_Menu_Categories(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            data=FoodCategories.objects.filter(user_id=id,status='live')
            return render(request,'admin/menu/categories/show_category.html',{'data':data})

        else:
            return redirect('admin-login')
        
class Edit_Menu_Categories(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            data=FoodCategories.objects.get(id=id)
            return render(request,'admin/menu/categories/edit_category.html',{'data':data})

        else:
            return redirect('admin-login')
        
   
    def post(self,request,id):
        category_name=request.POST.get('category_name')
        data=FoodCategories.objects.get(id=id)
        FoodCategories(id=id,category_name=category_name,created_at=data.created_at,user_id=data.user_id,).save()
        return redirect('menu-details',data.user_id.id )
    
def delete_category(request,id):
    if request.user.is_authenticated:
            data=FoodCategories.objects.get(id=id)
            data.status='Delete'
            data.save()
            return redirect('menu-details',data.user_id.id )

    else:
        return redirect('admin-login')
    

class Show_Menu_food_items(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            data=FoodName.objects.filter(category_name=id).exclude(status='Delete')
            return render(request,'admin/menu/items/show_items.html',{'data':data})
            

        else:
            return redirect('admin-login')
        

class Edit_Menu_food_items(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            data=FoodName.objects.get(id=id)
            return render(request,'admin/menu/items/edit_items.html',{'data':data})
        else:
            return redirect('admin-login')
        
    def post(self,request,id):
        data=FoodName.objects.get(id=id)
        food_name=request.POST.get('food_name')
        food_image=request.FILES.get('food_image')
        full_price=request.POST.get('full_price')
        medium_price=request.POST.get('medium_price')
        small_price=request.POST.get('small_price')
        if food_image is not None:
            FoodName(id=id,category_name=data.category_name,food_name=food_name,food_image=food_image,full_price=full_price,medium_price=medium_price,small_price=small_price,created_at=data.created_at,user_id=data.user_id).save()
        else:
            FoodName(id=id,category_name=data.category_name,food_name=food_name,food_image=data.food_image,full_price=full_price,medium_price=medium_price,small_price=small_price,created_at=data.created_at,user_id=data.user_id).save()
        return redirect('show-menu-food',data.category_name.id)
    

def delete_item(request,id):
    if request.user.is_authenticated:
            data=FoodName.objects.get(id=id)
            data.delete()
            return redirect('show-menu-food',data.category_name.id )

    else:
        return redirect('admin-login')
    


class Add_Category_Image(View):
    def get(self,request):
        if request.user.is_authenticated:
                return render(request,'admin/catimage/addimage.html')
        else:
            return redirect('admin-login')
    def post(self,request):
        image=request.FILES.getlist('image')
        for image in image:
            CategoryImages.objects.create(image=image)
        return redirect('show-image')
    

class Show_Category_Image(View):
    def get(self,request):
        if request.user.is_authenticated:
                data=CategoryImages.objects.filter(user_id=None).order_by('-id')
                return render(request,'admin/catimage/showimage.html',{'data':data})
        else:
            return redirect('admin-login')
        

class Edid_Category_Image(View):
    def get(self,request,id):
        if request.user.is_authenticated:
                data=CategoryImages.objects.get(id=id)
                return render(request,'admin/catimage/editimage.html',{'data':data})
        else:
            return redirect('admin-login')
    def post(self,request,id):
        data=CategoryImages.objects.get(id=id)
        image=request.FILES.get('image')
        if image:
            data.image=image
            data.save()
        return redirect('show-image')
    
def deleteimage(request,id):
    if request.user.is_authenticated:
        data=CategoryImages.objects.get(id=id).delete()
        return redirect('show-image')
    else:
        return redirect('admin-login')
    


class User_Transaction_history(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            data=OrderPayment.objects.filter(users_id=CustomUser.objects.get(id=id))
            return render(request,'admin/users/user_transaction.html',{'data':data})
        else:
            return redirect('admin-login')
        
class Delete_User_Transaction(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            data=OrderPayment.objects.get(id=id)
            data.delete()
            return redirect('Tranaction_history',data.users_id.id)
        else:
            return redirect('admin-login')
        

class User_Orders(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            data=Order.objects.filter(user_id=CustomUser.objects.get(id=id)).order_by('-id')
            return render(request,'admin/user_order/show_order.html',{'data':data})
        else:
            return redirect('admin-login')




class Show_food_suggestions(View):
    def get(self,request):
        if request.user.is_authenticated:
            data=Food_Item_Suggestion.objects.all()
            return render(request,'admin/Food_suggestions/show_suggestions.html',{'data':data})
        else:
            return redirect('admin-login')




class Add_food_suggestions(View):
    def get(self,request):
        if request.user.is_authenticated:
            return render(request,'admin/Food_suggestions/add_suggestion.html')
        else:
            return redirect('admin-login')
    def post(self,request):
        name=request.POST.get('name')
        type=request.POST.get('type')
        Food_Item_Suggestion.objects.create(food_name=name,food_type=type)
        return redirect('show_suggestion')

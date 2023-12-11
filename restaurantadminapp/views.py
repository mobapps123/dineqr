from django.shortcuts import render,redirect,HttpResponse ,HttpResponseRedirect
from django.http import JsonResponse
from django.views import View
from django.contrib.auth import login , logout ,authenticate
from Adminapp.models import *
from .models import *
from django.contrib import messages
# from django.template.loader import get_template
# from xhtml2pdf import pisa
from datetime import date , timedelta
import stripe , json , os ,qrcode ,random
from django.conf import settings
from django.urls import reverse
from django.core.files import File
from io import BytesIO
from PIL import Image, ImageDraw
from django.db.models import Q
from datetime import datetime 
from twilio.rest import Client
from django.conf import settings
from cities_light.models import *
from countryinfo import CountryInfo
from babel.numbers import get_currency_symbol
from django.core.files.storage import default_storage
from geopy.geocoders import GoogleV3 
from geopy.distance import geodesic
from django.template.loader import get_template
# def get_address_from_lat_lon(api_key, latitude, longitude):
#     base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
#     # Set up the parameters for the API request
#     params = {
#         'latlng': f'{latitude},{longitude}',
#         'key': api_key,  # Replace with your Google Maps API key
#     }

#     # Make the API request
#     response = requests.get(base_url, params=params)
#     result = response.json()

#     # Check if the request was successful
#     if response.status_code == 200 and result['status'] == 'OK':
#         # Extract the formatted address from the result
#         formatted_address = result['results'][0]['formatted_address']
#         return formatted_address
#     else:
#         print(f"Error: {result['status']}")
#         return None
    
# Create your views here.
def calculate_distance(coord1, coord2):
    # coord1 and coord2 should be tuples containing (latitude, longitude)
    distance = geodesic(coord1, coord2).meters
    return distance


def get_lat_lon(address):
    geolocator = GoogleV3(api_key='AIzaSyDDI6643MQ-SLs7dwH12SzHg2DsuDVf07I')  # Replace with your API key

    location = geolocator.geocode(address)

    if location:
        latitude, longitude = location.latitude, location.longitude
        return latitude, longitude
    else:
        return None
    

# def symbol_to_currency_code(symbol):
#     currency_codes = CurrencyCodes()
#     try:
#         code = currency_codes.get_symbol(symbol)
#         if code:
#             return code
#         else:
#             return "Unknown"
#     except:
#         return "Error"
    
def get_currency_name(country_name):
    try:
        country_info = CountryInfo(country_name)
        currency_info = country_info.currencies()
        if currency_info:
            # Extract the currency name
            currency_name = currency_info[0]
            return currency_name
        else:
            print(f"No currency information available for {country_name}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


class Check_new_notification(View):
    def get(self,request):
        noti=Notification.objects.filter(receiver=request.user,read=False)
        noti_count=noti.count()
        print(noti_count,request.user.count1)
        if noti_count>request.user.count1:
            beep=1
        else:
            beep=0
        request.user.count1=noti_count
        request.user.save()
        
        data={'count':noti_count,'beep':beep}
        return JsonResponse(data)


class User_Login(View):
    def get(self,request):
        if not request.user.is_authenticated:
            if request.COOKIES.get('email') and request.COOKIES.get('pass'):
                cookie_value_email = request.COOKIES.get('email')
                cookie_value_pass = request.COOKIES.get('pass')
                cookie_value_check = request.COOKIES.get('check')
                return render(request,'restaurent_admin/login.html',{'cookie_value_email':cookie_value_email,'cookie_value_pass':cookie_value_pass,'cookie_value_check':cookie_value_check})
            else:
                return render(request,'restaurent_admin/login.html')
        else:
            # if  CustomUser.objects.filter(payment_status='Successfull',id=request.user.id).exists():
            return redirect('user-dashboard')
            # else:
            #     return redirect('subscription')
    def post(self,request):
        email=request.POST.get('email_id') 
        passwords=request.POST.get('password')
        email_id = email.lower()
        check=request.POST.get('checkbox_name')
        user = authenticate(
                request=request, email_id=email_id, password=passwords)
        if user is not None:
            if CustomUser.objects.filter(email_id=email_id, is_superuser=False):
                login(request, user)
                # if CustomUser.objects.filter(payment_status='Successfull',id=request.user.id).exists():
                if check=='True':
                    response=redirect('user-dashboard')
                    response.set_cookie('email', email_id)
                    response.set_cookie('pass', passwords)
                    response.set_cookie('check', check)
                    return response
                else:
                    if request.COOKIES.get('email') and request.COOKIES.get('pass'):
                        response=redirect('user-dashboard')
                        response.delete_cookie('email')
                        response.delete_cookie('pass')
                        response.delete_cookie('check')
                        return response
                    else:
                        return redirect('user-dashboard')
                    
                # else:
                #     if check=='True':
                #         response=redirect('subscription')
                #         response.set_cookie('email', email_id)
                #         response.set_cookie('pass', passwords)
                #         response.set_cookie('check', check)
                #         return response
                #     else:
                #         if request.COOKIES.get('email') and request.COOKIES.get('pass'):
                #             response=redirect('subscription')
                #             response.delete_cookie('email')
                #             response.delete_cookie('pass')
                #             response.delete_cookie('check')
                #             return response
                #         else:
                #             return redirect('subscription')
                    
            else:
                messages.warning(request, 'You Are Not User')
        else:
            messages.warning(request, 'Incorrect Password')
        return redirect('user-login')
    
class UserDashboard(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.is_superuser is False:
                data1=CustomUser.objects.get(id=request.user.id)
                # if data1.payment_status=='Successfull':
                #     time=date.today()
                #     newt=str(time)
                #     if newt > data1.subscritpion_expire_date:
                #         data1.payment_status='pending'
                #         data1.save()              
                # if CustomUser.objects.filter(payment_status='Successfull',id=request.user.id).exists():
                cat=FoodCategories.objects.filter(user_id=request.user,status='live')
                category=cat.count()
                item=FoodName.objects.all().filter(user_id=request.user).exclude(status='Delete').count()
                noti=Notification.objects.all().filter(receiver=request.user,read=False).count()
                cat_image=CategoryImages.objects.filter(user_id=None)
                cat_custom_image=CategoryImages.objects.filter(user_id=request.user)
                visitors=User_unique_id.objects.filter(user_id=request.user).count()
                order=Order.objects.filter(user_id=request.user).count()
                
                return render(request,'restaurent_admin/dashboard.html',context= {'category':category,'item':item,'noti':noti,'rname':data1,'cat':cat,'cat_image':cat_image,'visitors':visitors,'model':FoodCategories,'order':order,'cat_custom_image':cat_custom_image,'active':'active1'})
                # else:
                #     return redirect('subscription')
                
            else:
                return redirect('admin-login')
            
        else:        
            return redirect('user-login')
        


def userlogout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,'Log Out Successfully')
        return redirect('user-login')

    else:
        return redirect('user-login')
    



class Change_password(View):
    
    def post(self, request):
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        new_password = confirm_password
        user = CustomUser.objects.get(id=request.user.id)
        check=user.check_password(old_password)
        if check==True:
            user.set_password(new_password)
            user.save()
            user = authenticate(request, email_id=user.email_id, password=new_password)
            if user:
                login(request, user)
            messages.success(request, 'Password Change Successfully..!!')

            return redirect('restaurant-details')
        else:
            messages.error(request, 'Incorrect Old Password..!!')
    
        return redirect('restaurant-details')

class UserRegistration(View):
    def get(self,request):
        if not request.user.is_authenticated:
            return render(request,'restaurent_admin/registration.html',)
        else:
            return redirect('user-login')
        
    def post(self,request):
        rname=request.POST.get('Rname')
        email_id=request.POST.get('email_id')
        restaurant_address=request.POST.get('restaurant_address')
        full_name=request.POST.get('full_name')
        phone=request.POST.get('phone')
        password=request.POST.get('password')
        if not CustomUser.objects.filter(email_id=email_id).exists():
            data=CustomUser.objects.create_user(email_id=email_id,password=password,restaurant_name=rname,full_name=full_name,restaurant_address=restaurant_address,phone_number=phone)
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
            data.save()
            messages.success(request,'Account create Successfully!!!')
            return redirect('user-login')
        else:
            messages.warning(request,'This email has already been used')
            return redirect('user-registration')


    

class Add_Category(View):
    def post(self,request):
        category_name=request.POST.get('category_name')
        category_image=request.POST.get('category_image')
        custom_category_image=request.FILES.get('custom_category_image')
        category_type=request.POST.get('cat_type')
        print(custom_category_image)
        if FoodCategories.objects.filter(user_id=request.user,category_name=category_name,status='live').exists():
            messages.error(request,"This Category Already Exists")
            return redirect('user-dashboard')
        else:
            if category_image:
                data=CategoryImages.objects.get(id=category_image)
                FoodCategories.objects.create(category_name=category_name,category_image=data.image ,user_id=request.user,cat_type=category_type)
            elif custom_category_image:
                FoodCategories.objects.create(category_name=category_name,category_image=custom_category_image ,user_id=request.user,cat_type=category_type)
            else:
                FoodCategories.objects.create(category_name=category_name,user_id=request.user,cat_type=category_type)
            messages.success(request,'Category has been created')
            return redirect('user-dashboard')
    
class Show_Category(View):
    def get(self,request):
        if request.user.is_authenticated:
            data1=CustomUser.objects.get(id=request.user.id)
            # time=date.today()
            # newt=str(time)
            # if newt > data1.subscritpion_expire_date:
            #     data1.payment_status='pending'
            #     data1.save()
            #     return redirect('subscription')
            # else:
            data=FoodCategories.objects.filter(user_id=data1,status='live')
            return render(request,'restaurent_admin/add_categories/show_category.html',{'data':data,'rname':data1})

        else:
            return redirect('user-login')
    
class Edit_Category(View): 
    def post(self,request):

        category_name=request.POST.get('category_name')
        id=request.POST.get('cat_id')
        category_image=request.POST.get('change_imageee')
        category_type=request.POST.get('cat_type')
        data=FoodCategories.objects.get(id=id)
        if category_image:
            dataa=CategoryImages.objects.get(id=category_image)
            data.category_image=dataa.image
        data.category_name=category_name
        data.cat_type=category_type
        data.save()
        messages.success(request,'Update Successfully!!!')
        return redirect('user-dashboard')
    
class caterogy_details(View):
    def get(self,request):
        id=request.GET.get('id')
        data2=FoodCategories.objects.get(id=id)
        if data2.category_image != "":
            image_path = os.path.join('/media/', str(data2.category_image))
        else:
            image_path = os.path.join('/static/', 'images/food1.png')
        data={'category_name':data2.category_name,'image':image_path,'type':data2.cat_type}
        return JsonResponse(data)
    

def delete_category(request):
    if request.user.is_authenticated:
        user_id = request.GET.getlist('checkid')
        data_list = json.loads(user_id[0])
        data=FoodCategories.objects.filter(id__in=data_list)
        for data in data:
            data.status='Delete'
            data.save()
            food=FoodName.objects.filter(category_name=data)
            for food in food:
                food.status='Delete'
                food.save()
        return JsonResponse({'msg':'Category Deleted'})
    else:
        return redirect('user-login')


class Add_Item(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            cat=FoodCategories.objects.get(id=id)
            data1=CustomUser.objects.get(id=cat.user_id.id)
            # time=date.today()
            # newt=str(time)
            # if newt > data1.subscritpion_expire_date:
            #     data1.payment_status='pending'
            #     data1.save()
            #     return redirect('subscription')
            # else:
            Addons_Group.objects.filter(foodname=None,user_id=data1).delete()
            AddOnes.objects.filter(group_name=None,user_id=data1).delete()
            if cat.cat_type == 'Food':
                suggestion=Food_Item_Suggestion.objects.filter(food_type='Food')
            else:
                suggestion=Food_Item_Suggestion.objects.filter(food_type='Drinks')
            categories=FoodCategories.objects.filter(user_id=request.user,status='live').exclude(id=cat.id)
            return render(request,'restaurent_admin/add_items/add_item.html',{'rname':data1,'cat':cat,'categories':categories,'model':Top_Choices,'model2':FoodLevel,'model3':Addons_Group,'suggestion':suggestion})
        else:
            return redirect('user-login')
    def post(self,request,id):
        food_name=request.POST.get('food_name')
        food_image=request.FILES.get('food_image')
        price=request.POST.get('price')
        description=request.POST.get('description')
        category=request.POST.get('category')
        top_choice=request.POST.get('top_choice')
        incluted=request.POST.getlist('incluted')
        levels=request.POST.getlist('levels')
        discount=request.POST.get('discount')
        button=request.POST.get('submit_button')
        text_color=request.POST.get('text_color')
        background_color=request.POST.get('background_color')
        if button == 'publish':
            status='Publish'
        else:
            status="Save"
        if category:
            data=FoodCategories.objects.get(id=category)
        else:
            data = FoodCategories.objects.get(id=id)
        all_details = {
            'food_name':food_name ,
            'food_image':food_image ,
            'price':price,
            'description':description ,
            'category_name':data,
            'user_id':request.user,
            'status':status,
        }
        if data.cat_type == 'Drinks':
            all_details['text_color_type']=text_color
            all_details['background_color_type']=background_color
        if discount:
            discount_price= (float(price)*float(discount))/100
            all_details['discountPrice']=float(price)-discount_price
            all_details['discount']=discount
        name=FoodName(**all_details)
        name.save()   
        if incluted:
            for include in incluted:
                foodincludes.objects.create(name=include,food_name=name)
                Food_Item_Suggestion.objects.get_or_create(food_name=include,food_type=data.cat_type)
        group_adon=Addons_Group.objects.filter(user_id=request.user,foodname=None)
        if group_adon:
            for group in group_adon:
                Addons_Group.objects.filter(id=group.id,status=1).update(foodname=name)
        if levels:
            for level in levels:
                if data.cat_type == 'Food':
                    FoodLevel.objects.create(food_level=level,food_name=name)
                else:
                    FoodLevel.objects.create(drinks_level=level,food_name=name)
        if top_choice:
            if Top_Choices.objects.filter(top_choice=top_choice,user_id=data.user_id).exists():
                Top_Choices.objects.filter(top_choice=top_choice).update(foodname=name,user_id=data.user_id)
            else:
                Top_Choices.objects.create(top_choice=top_choice,foodname=name,user_id=data.user_id)
        if button== 'publish':
            return redirect('show-all-item',data.id)
        else:
            return redirect('show-all-draft-item',data.id)


class Adons_group(View):
    def get(self,request):
        datas=Addons_Group.objects.filter(foodname=None,user_id=request.user,status=1)
        context=[]
        context2=[]
        for data in datas:
            d={
                'group_name':data.group_name,   
                'group_type':data.group_type,
                'instruction':data.instruction,
                'id':data.id
            }
            context.append(d)
            adon_name=AddOnes.objects.filter(group_name=data,status=1)
            for adon in adon_name:
                c={
                    'name':adon.name,
                    'price':adon.price,
                    'id':adon.id,
                    'group_id':adon.group_name.id
                }
                context2.append(c)

        print(context)
        print(context2)
        return JsonResponse({'data':context,'data2':context2})
    def post(self, request):
        instruction=request.POST.get('instruction')
        selectedValue=request.POST.get('selectedValue')
        group_name=request.POST.get('group_name')
        food_id=request.POST.get('food_id')
        if food_id:
            food=FoodName.objects.get(id=food_id)
            group=Addons_Group.objects.create(instruction=instruction,group_type=selectedValue,group_name=group_name,user_id=request.user,foodname=food)
        else:
            group=Addons_Group.objects.create(instruction=instruction,group_type=selectedValue,group_name=group_name,user_id=request.user)
        addons=AddOnes.objects.filter(group_name=None,user_id=request.user)
        for addon in addons:
            AddOnes.objects.filter(id=addon.id).update(group_name=group)
        return JsonResponse({'msg':'Created'})

class Delete_Groups(View):
    def post(self,request,id):
        group=Addons_Group.objects.get(id=id)
        print(group)
        group.status=0
        group.save()
        adons=AddOnes.objects.filter(group_name=group)
        for adon in adons:
            print('asdc')
            AddOnes.objects.filter(id=adon.id).update(status=0)
        return JsonResponse({"msg":"Deleted"})


class Add_Once(View):
    def get(self,request,id):
        data=AddOnes.objects.filter(group_name=None,status=1,user_id=request.user)
        context=[]
        for data in data:
            d={
                'name':data.name,
                'id':data.id,

            }
            if data.price:
                d['price']=data.price
            context.append(d)
        context_data={'status':'success','data':context}
        return JsonResponse(context_data)
    def post(self,request,id):
        name=request.POST.get('name')
        price=request.POST.get('price')
        print(price)
        all_details={
            'name':name,
            'user_id':request.user
        }
        # if id != 0:
        #     food_item=FoodName.objects.get(id=id)
        #     all_details['foodname']=food_item
        if price:
            all_details['price']=float(price)
        addons=AddOnes(**all_details)
        addons.save()
        return JsonResponse({'msg':'Created'})
    

class Delete_Add_Once(View):
    def get(self,request,id):
        a=AddOnes.objects.get(id=id)
        a.status=0
        a.save()
        if a.group_name:
            status='true'
        else:
            status='false'
        context={'status':status}
        return JsonResponse(context)

class Show_Item(View):
    def post(self,request,id):
        item_id=request.POST['cat_id']
        items=FoodName.objects.get(id=item_id)
        groups=Addons_Group.objects.filter(foodname=items,user_id=request.user,status=1)
        context1=[]
        for group in groups:
            addonce=AddOnes.objects.filter(group_name=group,user_id=request.user,status=1).order_by('id')
            for add in addonce:
                d={
                    'name':add.name,
                    'price':add.price
                }
                context1.append(d)
        if items.user_id.currency:
            currency=items.user_id.currency
        else:
            currency='$'
        url = reverse('edit-item', args=[str(items.id)])
        context={'id':items.id,'name':items.food_name,'description':items.description,'price':items.price,'url':url,'data':context1,'currencys':currency}
        print(context)
        if items.food_image:
            src="/media/"+str(items.food_image)
            context['image']=src
        if items.background_color_type and items.text_color_type:
            context['background_color']=items.background_color_type
            context['text_color']=items.text_color_type

        return JsonResponse(context)

class Edit_Item(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            data1=CustomUser.objects.get(id=request.user.id)
            # time=date.today()
            # newt=str(time)
            # if newt > data1.subscritpion_expire_date:
            #     data1.payment_status='pending'
            #     data1.save()
            #     return redirect('subscription')
            # else:
            data=FoodName.objects.get(id=id)
            level=FoodLevel.objects.filter(food_name=data)
            context2=[]
            if level.exists():
                for level in level:
                    if data.category_name.cat_type == 'Food':
                        d=level.food_level
                    else:
                        d=level.drinks_level
                    context2.append(d)
            Addons_Group.objects.filter(foodname=None,user_id=data1).delete()
            AddOnes.objects.filter(group_name=None,user_id=data1).delete()
            category=FoodCategories.objects.filter(user_id=request.user,status='live').exclude(id=data.category_name.id)
            adon_group=Addons_Group.objects.filter(user_id=request.user,foodname=data,status=1)
            print(adon_group)
            includes=foodincludes.objects.filter(food_name=data)
            if foodincludes.objects.filter(food_name=data).exists():
                inlcude_add=foodincludes.objects.filter(food_name=data)
                context=[]
                for inlcude_add in inlcude_add:
                    context.append(inlcude_add.name)
                item_suggestion=Food_Item_Suggestion.objects.exclude(food_name__in=context)  
            else:
                # item_suggestion=Food_Item_Suggestion.objects.all()
                if data.category_name.cat_type == 'Food':
                    item_suggestion=Food_Item_Suggestion.objects.filter(food_type='Food')
                else:
                    item_suggestion=Food_Item_Suggestion.objects.filter(food_type='Drinks')
            if Top_Choices.objects.filter(foodname=data,user_id=request.user).exists():
                top=Top_Choices.objects.get(foodname=data,user_id=request.user)
            else:
                top=1
            return render(request,'restaurent_admin/add_items/edit_item.html',{'data':data,'rname':data1,'top':top,'category':category,'model':Top_Choices,'model2':FoodLevel,'context2':context2,'model3':Addons_Group,'adon_group':adon_group,'item_suggestion':item_suggestion,'includes':includes})
        else:
            return redirect('user-login')
    def post(self,request,id):
        data=FoodName.objects.get(id=id)
        food_name=request.POST.get('food_name')
        food_image=request.FILES.get('food_image')
        price=request.POST.get('price')
        description=request.POST.get('description')
        button=request.POST.get('submit_button')
        category=request.POST.get('category')
        top_choice=request.POST.get('top_choice')
        levels=request.POST.getlist('levels')
        incluted=request.POST.getlist('include')
        discount=request.POST.get('discount')
        text_color=request.POST.get('text_color')
        background_color=request.POST.get('background_color')
        FoodLevel.objects.filter(food_name=data).delete()
        foodincludes.objects.filter(food_name=data).delete()
        if levels:
            for level in levels:
                if data.category_name.cat_type == 'Food':
                    FoodLevel.objects.create(food_level=level,food_name=data)
                else:
                    FoodLevel.objects.create(drinks_level=level,food_name=data)
        if category:
            f_cat=FoodCategories.objects.get(id=category)
        else:
            f_cat = FoodCategories.objects.get(id=data.category_name.id)
        if incluted:
            for include in incluted:
                foodincludes.objects.create(name=include,food_name=data)
                Food_Item_Suggestion.objects.get_or_create(food_name=include,food_type=f_cat.cat_type)
        if data.is_active==1:
            if top_choice and button=="publish":
                if Top_Choices.objects.filter(foodname=data,user_id=f_cat.user_id).exists():
                    Top_Choices.objects.filter(foodname=data,user_id=f_cat.user_id).delete()
                if Top_Choices.objects.filter(top_choice=top_choice,user_id=f_cat.user_id).exists():
                    Top_Choices.objects.filter(top_choice=top_choice).update(foodname=data,user_id=f_cat.user_id)
                else:
                    Top_Choices.objects.create(top_choice=top_choice,foodname=data,user_id=f_cat.user_id)
            else:
                if Top_Choices.objects.filter(foodname=data,user_id=f_cat.user_id).exists():
                    Top_Choices.objects.filter(foodname=data,user_id=f_cat.user_id).delete()
        if button == 'publish':
            status='Publish'
        else:
            status="Save"
        if food_image is not None:
            data.food_image=food_image

        if discount:
            discount_price= (float(price)*float(discount))/100
        else:
            discount=0
            discount_price= (float(price)*float(discount))/100
        if text_color and background_color:
            data.text_color_type=text_color
            data.background_color_type=background_color
        data.discountPrice=float(price)-discount_price
        data.discount=discount
        data.food_name=food_name
        data.description=description
        data.status=status
        data.price=price
        data.category_name=f_cat
        data.save()
        if button== 'publish':
            return redirect('show-all-item',data.category_name.id)
        else:
            return redirect('show-all-draft-item',data.category_name.id)
        

class Delete_item(View):
    def post(self,request):
        if request.user.is_authenticated:
            user_id = request.POST.getlist('checkid')
            data_list = json.loads(user_id[0])
            data=FoodName.objects.filter(id__in=data_list)
            for data in data:
                data.status='Delete'
                data.save()
                if Top_Choices.objects.filter(foodname=data,user_id=request.user).exists():
                    Top_Choices.objects.filter(foodname=data,user_id=request.user).delete()
            return redirect('show-all-item',data.category_name.id)
        else:
            return redirect('user-login')
class Show_all_items(View):
    def get(self,request,cat_ids):
        if request.user.is_authenticated:
            data1=CustomUser.objects.get(id=request.user.id)
            # time=date.today()
            # newt=str(time)
            # if newt > data1.subscritpion_expire_date:
            #     data1.payment_status='pending'
            #     data1.save()
            #     return redirect('subscription')
            # else:
            data=FoodCategories.objects.filter(user_id=request.user,status='live')
            
            if cat_ids != 0:
                first=FoodCategories.objects.get(id=cat_ids).category_name
                print('ac')
            else:
                if data:
                    first=data.first().category_name
                else:
                    first=None
            return render(request,'restaurent_admin/add_items/all_items.html',{'data':data,'rname':data1,'first':first,'active1':'active1'})
        else:
            return redirect('user-login')

class Show_all_draft_items(View):
    def get(self,request,cat_ids):
        if request.user.is_authenticated:
            data1=CustomUser.objects.get(id=request.user.id)
            # time=date.today()
            # newt=str(time)
            # if newt > data1.subscritpion_expire_date:
            #     data1.payment_status='pending'
            #     data1.save()
            #     return redirect('subscription')
            # else:
            data=FoodCategories.objects.filter(user_id=request.user,status='live')
            if cat_ids != 0:
                first=FoodCategories.objects.get(id=cat_ids).category_name
            else:
                if data:
                        first=data.first().category_name
                else:
                    first=None
            return render(request,'restaurent_admin/add_items/draft_items.html',{'data':data,'rname':data1,'first':first})
        else:
            return redirect('user-login')
    

    
class Add_Item_all(View):
    def get(self,request):
        if request.user.is_authenticated:
            data1=CustomUser.objects.get(id=request.user.id)
            # time=date.today()
            # newt=str(time)
            # if newt > data1.subscritpion_expire_date:
            #     data1.payment_status='pending'
            #     data1.save()
            #     return redirect('subscription')
            # else:
            data=FoodCategories.objects.filter(user_id=data1.id,status='live')
            return render(request,'restaurent_admin/add_items/add_all_items.html',{'data':data,'rname':data1})
        else:
            return redirect('user-login')
    def post(self,request):
        food_name=request.POST.get('food_name')
        food_image=request.FILES.get('food_image')
        price=request.POST.get('price')
        description=request.POST.get('description')
        button=request.POST.get('submit_button')
        category=request.POST.get('category')
        data=FoodCategories.objects.get(id=category)
        if button=='publish':
            status='Publish'
        else:
            status='Save'
        name=FoodName.objects.create(food_name=food_name,food_image=food_image,price=price,description=description,category_name=data,user_id=request.user,status=status)
        return redirect('edit-item',name.id)


class Restaurant_details(View):
    def get(self,request):
        if request.user.is_authenticated:
            data1=CustomUser.objects.get(id=request.user.id)
            typee=Restaurnt_type.objects.get(user=data1)
            print(typee.restaurant_type)
            # if data1.payment_diable_enable_status == 'False':
            #     check='false'
            # else:
            #     check='true'
            # time=date.today()
            # newt=str(time)
            # if newt > data1.subscritpion_expire_date:
            #     data1.payment_status='pending'
            #     data1.save()
            #     return redirect('subscription')
            # else:
            country=Country.objects.all().exclude(name=request.user.country)
            if data1.country:
                country_add=Country.objects.get(name=data1.country)
            else:
                country_add=None
            all_state=Region.objects.filter(country_id=country_add).exclude(name=data1.state)
            if data1.state:
                state=Region.objects.get(name=data1.state,country_id=country_add.id)
            else:
                state=0
            all_city=City.objects.filter(region_id=state).exclude(name=data1.city)
            if data1.city:
                city=City.objects.get(name=data1.city,region_id=state.id)
            else:
                city=None
            if Account_id.objects.filter(user=data1).exists():
                account=Account_id.objects.get(user=data1)
                print(account.is_active)
                if account.account_id:
                    account.status = True
                    account.save()
                    account_check = stripe.Account.retrieve(account.account_id)
                    print(account_check)
                    individual = account_check.get('individual')
                    if individual:
                        verification_status = individual.get('verification', {}).get('status')
                        print(verification_status)
                        if verification_status == 'verified':
                            verify = True
                        else:
                            verify = False
                    else:
                        # Handle the case where 'individual' is not present in the response
                        verify = False
                else:
                    verify=None
            else:
                account=Account_id.objects.create(user=data1)
                verify=None
            
            if Account_details.objects.filter(user=data1):
                account_details =Account_details.objects.get(user=data1)
            else:
                account_details = None 
            return render(request,'restaurent_admin/restaurant_details/restaurant_profile.html',{'rname':data1,'country':country,'country_add':country_add,'state':state,'all_state':all_state,'city':city,'all_city':all_city,'active4':'active1','account':account,'accounts':Account_details,'account_details':account_details,'verify':verify,'typee':typee,'model':Restaurnt_type})
        else:
            return redirect('user-login')
        
    def post(self,request):
        rname=request.POST.get('restaurant_name')
        rlogo=request.FILES.get('restaurant_logo')
        address=request.POST.get('restaurant_address')
        phone_number=request.POST.get('phone_number')
        country=request.POST.get('country')
        code=request.POST.get('code')
        email=request.POST.get('email')
        city=request.POST.get('city')
        state=request.POST.get('state')
        banner_image=request.FILES.get('banner_image')
        open_time=request.POST.get('open_time')
        close_time=request.POST.get('close_time')
        restaurant_type=request.POST.get('restaurant_type')
        print(restaurant_type)
        data=CustomUser.objects.get(id=request.user.id)
        typee=Restaurnt_type.objects.get(user=data)
        typee.restaurant_type=restaurant_type
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
        if rlogo is not None:
            data.restaurant_logo=rlogo
        if banner_image:
            data.banner_image=banner_image
        if state:
            data.state=Region.objects.get(id=state).name
        else:
            data.state=None
            data.city=None
        if city:
            data.city=City.objects.get(id=city).name
        if code != '':  
            data.Postal_code=code
        if country:
            data.country=Country.objects.get(id=country).name
        data.email_id=email
        data.restaurant_name=rname
        data.restaurant_address=address
        data.phone_number=phone_number
        data.open_time=open_time
        data.close_time=close_time
        data.save()
        messages.success(request,'Profile Updated!!')
        return redirect('restaurant-details')

class Remove_banner(View):
    def post(self,request):
        data=CustomUser.objects.get(id=request.POST.get('idd'))
        if data.banner_image:
            image=data.banner_image
            image.delete()
            data.save()
        return JsonResponse({'msg':'Delete'})

    

class DeleteImage(View):
    def post(self,request):
        id=request.POST.get('id')
        data=CustomUser.objects.get(id=id)
        data.restaurant_logo.delete()
        data.restaurant_logo=None
        data.save()
        JsonResponse('Deleted')


# class Restaurant_Menu(View):
#     def get(self,request,id):
#         if RestaurentDetails.objects.filter(user_id=int(id)).exists():
#             idd=RestaurentDetails.objects.get(user_id=int(id))
#             if idd.payment_status != 'pending':
        
#                 catagory=FoodCategories.objects.filter(restaurant_id=idd)
                
#                 return render(request,'restaurent_admin/restaurent_menu.html', {'category':catagory,'idd':idd} )
#             else:
#                 return :Response("<h1>Page Not Found......<h1>")
#         else:
#             return HttpResponse("<h1>bad request...<h1>")
        

class Change_Item_status(View):
    def post(self,request,id):
        name=FoodName.objects.get(id=id)
        if name.is_active == 0:
            name.is_active=1
        else:
            name.is_active = 0
        name.save()
        if Top_Choices.objects.filter(foodname=name,user_id=request.user).exists():
            Top_Choices.objects.filter(foodname=name,user_id=request.user).delete()
        return JsonResponse({'msg':'Changed'})

class User_Subscription(View):
    
    def get(self,request):
        if request.user.is_authenticated:
            
            if CustomUser.objects.filter(payment_status='pending',id=request.user.id).exists():
                name=CustomUser.objects.get(id=request.user.id)
                package=SubscriptionDetails.objects.filter().first()
                feature=subscription_features.objects.filter(subscription=package)
                # basic=SubscriptionDetails.objects.get(heading='Basic')
                # premium=SubscriptionDetails.objects.get(heading='Premium')
                
                return render(request,'restaurent_admin/subscription.html',{'package':package,'name':name,'feature':feature})
                # return render(request,'restaurent_admin/subscription.html',{'standard':standard,'basic':basic,'premium':premium})
            else:
                return redirect('user-dashboard')

        else:
            return redirect('user-login')

    def post(self,request):
        data=CustomUser.objects.get(id=request.user.id)
        subscription_date=date.today()
        payment=request.POST.get('payment')   
        payments_choice=request.POST.get('payments_choice')
        subscritpion_expire_date=subscription_date+timedelta(days=360)
        data.subscritpion_expire_date=subscritpion_expire_date
        data.payment_price=payment
        data.subscription_date=subscription_date
        data.save()
        return redirect('Payment')



class Payment(View):
    def get(self,request):
        if request.user.is_authenticated:
            if CustomUser.objects.filter(payment_status='pending',id=request.user.id).exists():
                data=CustomUser.objects.get(id=request.user.id)
                client_id = settings.CLIENT_ID
                return render(request,'restaurent_admin/payment.html',{'data':data,'client_id':client_id})
            else:
                return redirect('user-dashboard')
        else:
            return redirect('user-login')
        
    def post(self,request):
        id=request.POST['id']
        data=CustomUser.objects.get(id=id)
        data.payment_status='Successfull'
        data.save()
        return redirect('user-dashboard')




class Receive_Notification(View):
    def get(self,request):
        if request.user.is_authenticated:
            data1=CustomUser.objects.get(id=request.user.id)
            # time=date.today()
            # newt=str(time)
            # if newt > data1.subscritpion_expire_date:
            #     data1.payment_status='pending'
            #     data1.save()
            #     return redirect('subscription')
            # else:
            data=Notification.objects.filter(receiver=request.user).order_by('-id')
            context=[]
            for data in data:
                status=Notification.objects.get(id=data.id)
                if status.order_id:
                    order=Order.objects.get(id=status.order_id)
                    order_id=data.order_id
                    item_instruction=order.item_instruction
                else:
                    order_id=None
                    item_instruction=None
                color_names = ["Red", "Green", "Blue"]
                random_color = random.choice(color_names)
                initials = ''.join(word[0] for word in data.sender.split())
                d={
                    "sender":data.sender,
                    "description":data.description,
                    "id":data.id,
                    'initials':initials,
                    'color':random_color,
                    'order_id':order_id,
                    'item_instruction':item_instruction,
                    'created_at':data.created_at,
                }
                context.append(d)
                
                status.read=True
                status.save()
            data1.count1=0
            data1.save()
            return render(request,'restaurent_admin/notification.html',{'data':context,'rname':data1})
        else:
            return redirect('user-login')
        

def delete_notification(request,id):
    if request.user.is_authenticated:
        if request.method=='POST':
            data=Notification.objects.get(id=id)
            data.delete()
        return redirect('receive-notification')
    else:
        return redirect('user-login')


class Remove_notification(View):
    def get(self,request,id):
        reciver=CustomUser.objects.get(id=id)
        Notification.objects.filter(receiver=reciver).update(status='remove')
        return redirect('user-dashboard')


# cat=FoodCategories.objects.filter(cat_type='Drinks')
# for cat in cat:
#     cat1=FoodCategories.objects.get(id=cat.id)
#     food=FoodName.objects.filter(category_name=cat1)
#     for food in food:
#         food.food_image=None
#         food.save()

class Notification_details(View):
    def get(self,request,id):
        if request.user.is_authenticated:
            data1=CustomUser.objects.get(id=request.user.id)
            order=Order.objects.get(id=id)
            order.item_instruction=False
            order.save()
            user=UserDetails.objects.get(order_id=order)
            color_names = ["Red", "Green", "Blue"]
            random_color = random.choice(color_names)
            initials = ''.join(word[0] for word in user.name.split())
            all_orders=Allorders.objects.filter(order_id=order)
            total_all_order=[]
            for all_order in all_orders:
                adons=FoodAdd.objects.filter(order_id=Allorders.objects.get(id=all_order.id))
                group_context = []
                adon_context=[]
                if adons:
                    print('hello')
                    for adon in adons:
                        group_context.append(adon.addonce_id.group_name.id)
                        adon_context.append(adon.addonce_id.id)
                    unique_list = list(set(group_context))
                    group=Addons_Group.objects.filter(id__in=unique_list)
                else:
                    group=None
                d={
                    'id':all_order.id,
                    'adon_context':adon_context,
                    'group':group
                }
                total_all_order.append(d)
            print(total_all_order)
            return render(request,'restaurent_admin/notification_details.html',{'rname':data1,'order':order,'total_all_order':total_all_order,'random_color':random_color,'initials':initials,'user':user})
        else:
            return redirect('user-login')


def generate_pdf(request, id):
    # Get the CustomUser object
    data = CustomUser.objects.get(id=id)

    # Check if the user has a QR code associated with their profile
    if data.qr_code:
        # Get the file path associated with the ImageField
        image_path = data.qr_code.path

        # Check if the image file exists
        if default_storage.exists(image_path):
            with default_storage.open(image_path, 'rb') as image_file:
                response = HttpResponse(image_file.read(), content_type='image/jpeg')  # Adjust the content type based on your image type (e.g., 'image/png')
                response['Content-Disposition'] = f'attachment; filename="{data.qr_code.name}"'
                return response

    return HttpResponse('Image not found', status=404)
    

class TermandConditions(View):
    def get(self,request):
        data=Termandcondition.objects.all()
        return render(request,'restaurent_admin/termandcondition.html',{'data':data})
class Privacyandpolicies(View):
    def get(self,request):
        data=PrivacyAndPolicy.objects.all()
        return render(request,'restaurent_admin/privcayandpolicy.html',{'data':data})
    



class Show_cat_image(View):
    def get(self,request):
        id=request.GET['id']
        img=CategoryImages.objects.get(id=id)
        imag=img.id
        src="/media/"+str(img.image)

        data={'cat_image':src,'image':imag}
        return JsonResponse(data) 

class Order_history(View):
    def get(self,request):
        if request.user.is_authenticated:
            data1=CustomUser.objects.get(id=request.user.id)
            order=Order.objects.filter(user_id=data1).order_by('-id')
            restaurant_type=Restaurnt_type.objects.get(user=data1)
            return render(request,'restaurent_admin/order_history.html',{'order':order,'rname':data1,'active2':'active1','restaurant_type':restaurant_type})
        else:
            return redirect('user-login')


class Completeorder(View):
    def post(self,request):
        order_id=request.POST.get('id')
        order_name=request.POST.get('order_name')
        order=Order.objects.get(id=order_id)
        user=UserDetails.objects.get(order_id = order)
        print(user.phone_number,type(user.phone_number))
        print(settings.TWILIO_ACCOUNT_SID)
        print(settings.TWILIO_AUTH_TOKEN)
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        # Create a Twilio client
        client = Client(account_sid, auth_token)
        # Send an SMS
        print(request.user.country,'country')
        if request.user.country == 'Nigeria':
            number = '+234'+str(user.phone_number)
        elif request.user.country == 'United States':
            number = '+1'+str(user.phone_number)
        elif request.user.country == 'India':
            number = '+91'+str(user.phone_number)
        
        print(number)
        message1 = client.messages.create(
            messaging_service_sid='MG10a8112c8e7c072acd7783cb7851ae5f',
            to='number',
            body=f'Great news! Your order {order.id} from {request.user.restaurant_name} is now ready for pickup. Enjoy your meal!',
        )
        print(f'Your order {order.id} from {request.user.restaurant_name} is now ready for pickup. Enjoy your meal!')
        order.status='Order_sent'
        order.save()
        if order_name:
            return redirect('user_order',order.user_id.id)
        return redirect('order_history')



class Transaction_History(View):
    def get(self,request):
        if request.user.is_authenticated:
            data1=CustomUser.objects.get(id=request.user.id)
            transaction=OrderPayment.objects.filter(users_id=data1).order_by('-id')
            return render(request,'restaurent_admin/transaction_history.html',{'transaction':transaction,'rname':data1,'active3':'active1'})
        else:
            return redirect('user-login')
        


class Delete_Transaction_History(View):
    def get(self,request):
        ids=request.GET.get('checkid')
        my_list = json.loads(ids)
        OrderPayment.objects.filter(id__in=my_list).delete()
        return JsonResponse({'msg':'Deleted Succesfully'})
  

class Custom_catgory_images(View):
    def get(self,request):
        images=CategoryImages.objects.filter(user_id=request.user).order_by('-id')
        context=[]
        for image in images:
            src="/media/"+str(image.image)
            d={
                'id':image.id,
                'image':src
            }
            context.append(d)
        return JsonResponse({'data':context})


    def post(self,request):
        uploaded_image = request.FILES.getlist('imagePath')
        print(uploaded_image,'abc')
        for uploaded in uploaded_image:
            print(uploaded)
            CategoryImages.objects.create(image=uploaded,user_id=request.user)
        return JsonResponse({'msg':'created'})

class Delete_custom_images(View):
    def post(self,request):
        idd=request.POST.get('id')
        print(idd)
        CategoryImages.objects.filter(id=idd).delete()
        return JsonResponse({'msg':'deleted'})



class Account_status(View):
    def get(self,request,id):
        account=Account_id.objects.get(user_id=CustomUser.objects.get(id=id))   
        account.status=True
        account.save()
        return redirect('restaurant-details')

class ConnectWithStripe(View):
    def get(self, request):
        account_detail=Account_details.objects.get(user=request.user)
        stripe.api_key = 'sk_test_51O5w34DBYJ1xxvlEX89NGZXPtZTR7z2xyADaWhIB5I7Zcmq9HzkCNz2NHF2l0sSiDdV1cEJKmV4cUAAoNHSY1Gv000TEEvbR6c'
        try:
            if request.user.country == 'Nigeria':
             # Create a Custom Connect account
                account = stripe.Account.create(
                    type="custom",
                    country="NG",
                    email=request.user.email_id,
                    capabilities={
                    "transfers": {"requested": True},
                    },
                    tos_acceptance={"service_agreement": "recipient"},
                ) 
            else:
                # Create a Custom Connect account
                account = stripe.Account.create(
                    type="custom",
                    country="US",
                    email=request.user.email_id,
                    capabilities={
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                    },
                ) 
            account_id=account['id']
            redirect_uri = 'http://127.0.0.1:8000/restaurant-details/'

            # Create a Standard account link
            account_link = stripe.AccountLink.create(
                account=account_id,  # Replace with your connected account ID
                refresh_url=redirect_uri,
                return_url=redirect_uri,
                type='account_onboarding',
            )
            if request.user.country == 'Nigeria':
                external_account=stripe.Account.create_external_account(
                account_id,
                    external_account={
                        'object': 'bank_account',
                        'country': 'NG',
                        'currency': 'NGN',
                        'account_number': account_detail.account_number,
                        'account_holder_name': account_detail.account_holder_name,
                        'account_holder_type': account_detail.account_holder_type, 
                        'routing_number': account_detail.routing_number,
                    }
                )
            else:
                external_account=stripe.Account.create_external_account(
                    account_id,
                    external_account={
                        'object': 'bank_account',
                        'country': 'US',
                        'currency': 'usd',
                        'account_number': account_detail.account_number,
                        'routing_number': account_detail.routing_number,
                        'account_holder_name': account_detail.account_holder_name,
                        'account_holder_type': account_detail.account_holder_type,  # or 'company' for business accounts
                    }
                )
            print(external_account.id)
            if Account_id.objects.filter(user_id=request.user).exists():
                Account_id.objects.filter(user_id=request.user).update(account_id=account_id,bank_id = external_account.id)
            else:
                Account_id.objects.create(user_id=request.user,account_id=account_id)
            return HttpResponseRedirect(account_link.url)
        except stripe.error.StripeError as e:
            print(f"Stripe Error: {e}")
            # Handle the error appropriately, e.g., return an error response to the user

        return HttpResponse("Failed to create Stripe account.")

class Edit_stripe_account(View):
    def get(self,request):
        account_id = Account_id.objects.get(user=request.user)
        account_id = account_id.account_id
        stripe.api_key = 'sk_test_51O5w34DBYJ1xxvlEX89NGZXPtZTR7z2xyADaWhIB5I7Zcmq9HzkCNz2NHF2l0sSiDdV1cEJKmV4cUAAoNHSY1Gv000TEEvbR6c'
        # Create a link for onboarding or edit
        redirect_uri = 'http://127.0.0.1:8000/restaurant-details/'
        account_link = stripe.AccountLink.create(
            account=account_id,
            refresh_url=redirect_uri,
            return_url=redirect_uri,
            type='account_onboarding',  # Use 'account_onboarding' for onboarding link or 'account_update' for edit link
        )
        link_url = account_link.url
        print(f'Redirect user to: {link_url}')
        return HttpResponseRedirect(link_url)



# CategoryImages.objects.filter(id__in=[117]).delete()            

def send_sms(request,id):
    # Your Twilio credentials from settings
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN

    # Create a Twilio client
    client = Client(account_sid, auth_token)
    print('hello')
    # Send an SMS
    message = client.messages.create(
        to='+918808278169',
        from_='+16195678345',
        
        body=f'Great news! Your order {id} from {request.user.restaurant_name} is now ready for pickup. Enjoy your meal!',
    )
    return redirect('order_history')
        

def Change_notification_status(request):
    noti=Notification.objects.filter(receiver=request.user,status='live').order_by('-id')
    noti.update(read=True)
    request.user.count1=0
    request.user.save()
    context=[]
    for noti in noti:
        # Parse the timestamp string
        timestamp = datetime.strptime(str(noti.created_at), "%Y-%m-%d %H:%M:%S.%f%z")
        # Format the date as a string
        date_str = timestamp.strftime("%Y-%m-%d")
        print(date_str)
        d={
            'id':noti.id,'description':noti.description,'sender':noti.sender,'created_at':date_str
        }
        context.append(d)
    print(context)
    return JsonResponse({'data':context})




class Table_status(View):
    def get(self,request):
        user=CustomUser.objects.get(id=request.user.id)
        if user.table_number_status==0:
            user.table_number_status=1
        else:
            user.table_number_status=0
        user.save()
        return JsonResponse({'msg':'chnage'})
        


class Account_Detail(View):
    def post(self,request):
        account_number=request.POST.get('account_number')
        account_holder_name=request.POST.get('account_holder_name')
        routing_number=request.POST.get('routing_number')
        account_holder_type=request.POST.get('account_holder_type')
        if Account_details.objects.filter(user = request.user).exists():
            account_details = Account_details.objects.get(user = request.user)
        else:
            account_details=Account_details()
            account_details.user = request.user
        account_details.account_holder_name=account_holder_name
        account_details.account_holder_type=account_holder_type
        account_details.account_number=account_number
        account_details.routing_number = routing_number
        account_details.save()
        return redirect('restaurant-details')


class Transfer_amount(View):
    def post(self,request):
        stripe.api_key = 'sk_test_51O5w34DBYJ1xxvlEX89NGZXPtZTR7z2xyADaWhIB5I7Zcmq9HzkCNz2NHF2l0sSiDdV1cEJKmV4cUAAoNHSY1Gv000TEEvbR6c'
        today_date=datetime.now().date()

        if OrderPayment.objects.filter(users_id = request.user , status = 'Pending',order_transfer_date=today_date):
            orders=OrderPayment.objects.filter(users_id = request.user , status = 'Pending',order_transfer_date=today_date)
            account_id=Account_id.objects.get(user=request.user)
            print(account_id.account_id)
            print('orders')
            total_amount=[]
            order_id=[]
            for order in orders:
                d=order.order_id.totalprice
                b=order.order_id.id
                order_id.append(b)
                total_amount.append(d)
            total_sum = sum(total_amount)
            final_price = round(total_sum,2)
            print(final_price)
            if request.user.country == 'Nigeria':
                transfer=stripe.Transfer.create(
                    amount=int(float(final_price) * 100),
                    currency="ngn",
                    destination=account_id.account_id,
                )
            else:
                transfer=stripe.Transfer.create(
                    amount=int(float(final_price) * 100),
                    currency="usd",
                    destination=account_id.account_id,
                    source_type= "card",
                )
            print(transfer)
            if transfer:
                Notification.objects.create(sender='DineQr',receiver=request.user,description=f'Your Stripe Acocunt has credit {final_price}, from order {order_id}')
                OrderPayment.objects.filter(users_id = request.user ,order_transfer_date=today_date).update(status = 'Received')
            Transfer_amount_details.objects.create(users_id=request.user,account_id=account_id.account_id,transfer_id=transfer.id,amount=final_price)
        else:
            print('no transfer')
        return JsonResponse({'msg':'Crated'})



################Mobile View############
class Mobile_home(View):
    def get(self,request,id):
        user=CustomUser.objects.get(id=id)
        restaurnt_type=Restaurnt_type.objects.get(user=user)
        print(restaurnt_type.restaurant_type)
        if user.is_active == True:
            if not request.session.session_key:
                request.session.create()
            unique_id = request.session.get('unique_id', None)
            if not unique_id:
                unique_id = str(request.session.session_key)
                request.session['unique_id'] = unique_id
            if not User_unique_id.objects.filter(unique_id=unique_id,user_id=user).exists():
                customer=User_unique_id.objects.create(unique_id=unique_id,user_id=user)
            else:
                customer=User_unique_id.objects.get(unique_id=unique_id,user_id=user)
            if  user.close_time:
                close_time = datetime.strptime(user.close_time, "%H:%M").time()
                formatted_time2 = close_time.strftime("%I:%M %p")
            else:
                formatted_time2=None
            
            if customer.order_type:
                order_type = True
            else:
                order_type = False
            data=FoodCategories.objects.filter(user_id=user,status='live')
            addtocart=Addtocart.objects.filter(user_id=user,unique_id=unique_id).count()
            if Top_Choices.objects.filter(top_choice="#1 favorite",user_id=user).exists():
                top1=Top_Choices.objects.get(top_choice="#1 favorite",user_id=user)
            else:
                top1='None'
            if Top_Choices.objects.filter(top_choice="#2 favorite",user_id=user).exists():
                top2=Top_Choices.objects.get(top_choice="#2 favorite",user_id=user)
            else:
                top2='None'
            if Top_Choices.objects.filter(top_choice="#3 favorite",user_id=user).exists():
                top3=Top_Choices.objects.get(top_choice="#3 favorite",user_id=user)
            else:
                top3='None'
            food_list=FoodName.objects.filter(user_id=user,status='Publish')
            return render(request,'mobile_view/home_page.html',{'data':data,'user':user,'id':unique_id, 'addtocart':addtocart,'top1':top1,'top2':top2,'top3':top3,'formatted_time2':formatted_time2,'customer':customer,'food_list':food_list,'restaurnt_type':restaurnt_type,'order_type':order_type})
        else:
            return HttpResponse('Service not found.....')
    def post(self,request,id):
        user=CustomUser.objects.get(id=id)
        user_idd=request.POST.get('user_id')
        order_type=request.POST.get('order_type')
        customer=User_unique_id.objects.get(unique_id=user_idd,user_id=user)
        
        customer.order_type=order_type
        customer.save()
        return redirect('mobile_home',id)



class Mobile_items(View):
    def get(self,request,id):
        if not request.session.session_key:
            request.session.create()
        unique_id = request.session.get('unique_id', None)
        if not unique_id:
            unique_id = str(request.session.session_key)  # Use session ID as unique identifier
            request.session['unique_id'] = unique_id
        cat=FoodCategories.objects.get(id=id)
        if User_unique_id.objects.filter(unique_id=unique_id,user_id=cat.user_id).exists():
            data=FoodName.objects.filter(category_name=cat,status='Publish')
            addtocart=Addtocart.objects.filter(user_id=cat.user_id,unique_id=unique_id).count()
            return render(request,'mobile_view/food_items.html',{'data':data,'cat':cat,'user':cat.user_id,'addtocart':addtocart})
        else:
            return redirect('mobile_home',cat.user_id.id)


class Mob_Item_details(View):
    def get(self,request,id):
        if not request.session.session_key:
            request.session.create()
        unique_id = request.session.get('unique_id', None)
        if not unique_id:
            unique_id = str(request.session.session_key)  # Use session ID as unique identifier
            request.session['unique_id'] = unique_id
        data=FoodName.objects.get(id=id)
        if User_unique_id.objects.filter(unique_id=unique_id,user_id=data.user_id).exists():
            level=FoodLevel.objects.filter(food_name=data)
            context=[]
            for level in level:
                if data.category_name.cat_type == 'Food':
                    lvel=level.food_level
                else:
                    lvel=level.drinks_level
                context.append(lvel)
            addonec=Addons_Group.objects.filter(foodname=data,status=1)
            addtocart=Addtocart.objects.filter(user_id=data.user_id,unique_id=unique_id).count()
            return render(request,'mobile_view/mob_item_detail.html',{'data':data,'user':data.user_id,'addtocart':addtocart,'addonec':addonec,'context':context,'id':unique_id})
        else:
            return redirect('mobile_home',data.user_id.id)
    def post(self,request,id):
        if not request.session.session_key:
            request.session.create()
        unique_id = request.session.get('unique_id', None)
        if not unique_id:
            unique_id = str(request.session.session_key)  # Use session ID as unique identifier
            request.session['unique_id'] = unique_id
        spicelevel=request.POST.get('selected_button')
        quantity=request.POST.get('quantity')   
        addonce=request.POST.getlist('addonnss')
        price=request.POST.get('price')
        food_instruction=request.POST.get('food_instruction')
        includes=request.POST.getlist('includes')
        data=FoodName.objects.get(id=id)
        addonec=Addons_Group.objects.filter(foodname=data,status=1)
        add_id=Addtocart.objects.create(user_id=data.user_id,unique_id=unique_id,spicelevel=spicelevel,food_id=data,quantity=quantity)
        if food_instruction:
            add_id.food_instruction=food_instruction
        if includes:
            for include in includes:
                FoodIncludes_add.objects.create(name=include,addtocart=add_id)
        if addonce:
            context=[]
            for addonce in addonce:
                addprice=FoodAddonce.objects.create(addonce_id=AddOnes.objects.get(id=addonce),user_id=data.user_id,food_id=data,unique_id=unique_id,addtocart=add_id)
                total_add_price=addprice.addonce_id.price
                context.append(total_add_price)
            all_context=sum(context)
        else:
            all_context=0
        total_item_price=float(quantity)*(float(price)+all_context) 
        add_id.price=total_item_price
        add_id.save()
        messages.success(request,'hello')
        return redirect('mobile_home', data.user_id.id)

class AddToCartView(View):
    def get(self,request,id):
        if not request.session.session_key:
        # Create a session to generate a unique session ID
            request.session.create()
    
        # Get or set the unique identifier in the session
        unique_id = request.session.get('unique_id', None)
        if not unique_id:
            unique_id = str(request.session.session_key)  # Use session ID as unique identifier
            request.session['unique_id'] = unique_id
        user=CustomUser.objects.get(id=id)
        restaurant_type = Restaurnt_type.objects.get(user=user)
        if User_unique_id.objects.filter(unique_id=unique_id,user_id=user).exists():
            if User_unique_id.objects.filter(user_id=user,unique_id=unique_id):
                mob_user=User_unique_id.objects.get(user_id=user,unique_id=unique_id)
            else:
                return redirect('mobile_home',id)
            details=Addtocart.objects.filter(user_id=user,unique_id=unique_id)
            allquanitty=[]
            allprice=[]
            data=[]
            for detail in details:
                if detail.quantity==1:
                    check=True
                elif detail.quantity==10:
                    check=False
                else:
                    check=0
                c=detail.quantity
                allquanitty.append(c)
                d=detail.price
                allprice.append(d)
                d={
                    'name' :detail.food_id.food_name,
                    'price':detail.price,
                    'spicelevel':detail.spicelevel,
                    'check':check,
                    'id':detail.id,
                    'quantity':detail.quantity,
                    'included':detail.food_id.included,
                }
                if detail.food_id.food_image:
                    d['image']=detail.food_id.food_image
                data.append(d)
            total_quantity=sum(allquanitty)
            total_price=sum(allprice)
            addtocart=details.count()
            service_fees=(total_price*user.service_fee)/100
            rounded_number = round(service_fees, 2)
            service_add_money=rounded_number+total_price
            if user.restaurant_address and user.city and user.state and user.country:
                address = user.restaurant_address+','+user.city +','+user.state+','+user.country
                result = get_lat_lon(address)
                if mob_user.latitude and mob_user.longitude:
                    coord1 = result  
                    coord2 = (mob_user.latitude, mob_user.longitude)
                    print(coord2)
                    distance = calculate_distance(coord1, coord2)
                    print(f"The distance between the two locations is {distance:.2f} meters.")
                else:
                    distance=None
            else:
                distance=None
            if Account_id.objects.filter(user=user,).exists():
                account=Account_id.objects.get(user=user)
                if account.account_id:
                    account_check = stripe.Account.retrieve(account.account_id)
                    verification_status = account_check['individual']['verification']['status']
                    if verification_status  == 'verified':
                        verify = True
                    else:
                        verify= False
                else:
                        verify= False
            else:
                verify=False
                account=None
            print(distance,'distance')
            return render(request,'mobile_view/addtocart.html',{'data':data,'user':user,'addtocart':addtocart,'allquanitty':total_quantity,'total_price':total_price,'mob_user':mob_user,'rounded_number':rounded_number,'service_add_money':service_add_money,'distance':distance,'restaurant_type':restaurant_type,'verify':verify,'account':account})
        else:
            return redirect('mobile_home',id)
    def post(self,request,id):
        if not request.session.session_key:
            request.session.create()
        unique_id = request.session.get('unique_id', None)
        if not unique_id:
            unique_id = str(request.session.session_key)  # Use session ID as unique identifier
            request.session['unique_id'] = unique_id
        user=CustomUser.objects.get(id=id)
        name=request.POST.get("name")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        tip_amount=request.POST.get("tip_amount")
        total_price=request.POST.get("total_price")
        table_number=request.POST.get('table_number')
        all_value={
            'name':name ,
            'email_id':email,
            'phone_number':phone,
            'total_price':total_price,
            'unique_id':unique_id,
            'user_id': user,
        }
        if table_number:
            all_value['table_number']=table_number
        print(tip_amount,'tip')
        if tip_amount:
            all_value['tip_amount']=tip_amount
        user_details = UserDetails(**all_value)
        user_details.save()
        return redirect('success-page',id)
    
class RemoveAddtocart(View):
    def get(self,request,id):
        data=Addtocart.objects.get(id=id)
        data.delete()
        return redirect('AddToCartView',data.user_id.id)
    
class ManageQuantity(View):
    def get(self,request):
        if not request.session.session_key:
        # Create a session to generate a unique session ID
            request.session.create()
    
        # Get or set the unique identifier in the session
        unique_id = request.session.get('unique_id', None)
        if not unique_id:
            unique_id = str(request.session.session_key)  # Use session ID as unique identifier
            request.session['unique_id'] = unique_id
        quantity=request.GET.get("quantity")
        id=request.GET.get("id")
        data=Addtocart.objects.get(id=id)
        addprice=FoodAddonce.objects.filter(unique_id=unique_id,addtocart=data)
        if addprice:
            context=[]
            for addprice in addprice:
                total_add_price=addprice.addonce_id.price
                context.append(total_add_price)
            all_context=sum(context)
        else:
            all_context=0
        if data.food_id.discountPrice == 0:
            price=data.food_id.price
        else:
            price = data.food_id.discountPrice
        total_item_price=float(quantity)*(price+all_context)
        data.quantity=quantity
        data.price=total_item_price
        data.save()     
        return redirect('AddToCartView',data.user_id.id)


stripe.api_key = 'sk_test_51O5w34DBYJ1xxvlEX89NGZXPtZTR7z2xyADaWhIB5I7Zcmq9HzkCNz2NHF2l0sSiDdV1cEJKmV4cUAAoNHSY1Gv000TEEvbR6c'


class CheckOutSession(View):
    def post(self, request, id):
        if not request.session.session_key:
            request.session.create()
        unique_id = request.session.get('unique_id', None)
        if not unique_id:
            unique_id = str(request.session.session_key)  # Use session ID as unique identifier
            request.session['unique_id'] = unique_id
        user=CustomUser.objects.get(id=id)
        name=request.POST.get("name")
        email=request.POST.get("email")
        phone=request.POST.get("phone")
        total_price=request.POST.get("total_price")
        payment_type=request.POST.get("payment_type")
        table_number=request.POST.get('table_number')
        tip_amount=request.POST.get("tip_amount")
        total_order_price=request.POST.get("total_order_price")
        stipe_type=request.POST.get("stipe_type")
        range1=request.POST.get("range")
        print('range1')
        all_value={
            'name':name ,
            'email_id':email,
            'phone_number':phone,
            'total_price':total_order_price,
            'unique_id':unique_id,
            'user_id': user,
            'customer_distance_range':range1
        }
        if stipe_type == 'off':
            all_value['restaurnt_payment_status'] = stipe_type
        if table_number:
            all_value['table_number']=table_number
        if user.country:
            country=user.country
            currency_name = get_currency_name(country)
        else:
            currency_name='USD'
        print(tip_amount,'tip')
        if tip_amount:
            all_value['tip_amount']=tip_amount
        if payment_type == 'online':
            all_value['payment_statud']=1
            user_defaults=UserDetails(**all_value)
            user_defaults.save()
            YOUR_DOMAIN = 'http://127.0.0.1:8000/'
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': currency_name,
                            'unit_amount': int(float(total_price) * 100),  # Stripe expects amount in cents
                            'product_data': {
                                'name': 'Total Amount',
                            },
                        },
                        'quantity':1,  # adjust quantity as needed
                    },
                ],
                mode='payment',
                success_url=YOUR_DOMAIN + 'Success-Page/'+str(id),
                cancel_url=YOUR_DOMAIN + 'add-to-cart-view/'+str(id),
                metadata={
                    'custom_data_key': 'custom_data_value',
                },
                customer_email=email,
                # payment_intent_data={
                #     'transfer_data': {
                #         'destination': 'acct_1OFvpvDA7bmXIfLx',  # Replace with the actual connected account ID
                #     },
                # },
            )

            return HttpResponseRedirect(checkout_session.url) 
        else:
            all_value['payment_statud']=0
            user_defaults=UserDetails(**all_value)
            user_defaults.save()
            return redirect('success-page',id)



class SuccessPage(View):
    def get(self,request,id):
        if not request.session.session_key:
            request.session.create()
        unique_id = request.session.get('unique_id', None)
        if not unique_id:
            unique_id = str(request.session.session_key)
            request.session['unique_id'] = unique_id
        user=CustomUser.objects.get(id=id)
        if User_unique_id.objects.filter(user_id=user,unique_id=unique_id):
            mob_user=User_unique_id.objects.get(user_id=user,unique_id=unique_id)
        details=Addtocart.objects.filter(user_id=user,unique_id=unique_id)
        if details.exists():
            addtocart=details.count()
            quantitys=[]
            try:
                users=UserDetails.objects.get(unique_id=unique_id,order_id=None)
            except UserDetails.MultipleObjectsReturned:
                users=UserDetails.objects.filter(unique_id=unique_id,order_id=None).last()
                UserDetails.objects.filter(unique_id=unique_id,order_id=None).exclude(id=users.id).delete()
            order_id=Order.objects.create(totalprice=0,quantity=0,user_id=user,customer_distance_range=users.customer_distance_range)
            if users.restaurnt_payment_status:
                order_id.restaurnt_payment_status=users.restaurnt_payment_status
            for detail in details:
                price=detail.price
                quantity=detail.quantity
                quantitys.append(int(quantity))
                if detail.food_id.discount != 0:
                    food_price=detail.food_id.discountPrice
                else:
                    food_price=detail.food_id.price
                allorder=Allorders.objects.create(order_id=order_id,user_id=user,food_id=detail.food_id,food_name=detail.food_id.food_name,food_image=detail.food_id.food_image,food_price=food_price,quantity=detail.quantity,spicelevel=detail.spicelevel,price=price)
                if detail.food_instruction:
                    allorder.food_instruction=detail.food_instruction
                    allorder.save()
                    order_id.item_instruction=True
                foodaddonce=FoodAddonce.objects.filter(unique_id=unique_id,addtocart=detail)
                if foodaddonce:
                    for addonce in foodaddonce:
                        food_adons=FoodAddonce.objects.get(id=addonce.id)
                        FoodAdd.objects.create(order_id=allorder,addonce_id=food_adons.addonce_id)
            if users.payment_statud == 1:
                status='Pending'
            else:
                status="By Cash"
                f_inlcude=FoodIncludes_add.objects.filter(addtocart=detail)
                for f in f_inlcude:
                    Selected_FoodIncludes_add.objects.create(name=f.name,order_id=allorder)

            payment=OrderPayment.objects.create(order_id=order_id,user=users,status=status,users_id=user)
            timestamp = datetime.strptime(str(payment.created_at), "%Y-%m-%d %H:%M:%S.%f%z")
            # Format the date as a string
            if payment.status == 'Pending':
                date_str = timestamp.strftime("%Y-%m-%d")
                print(date_str,type(date_str))
                data_date = datetime.strptime(date_str,'%Y-%m-%d')
                transfer_date= data_date + timedelta(days=4)
                payment.order_transfer_date=transfer_date
                payment.save()
            total_quantity=sum(quantitys)
            order_id.totalprice=users.total_price
            order_id.quantity=total_quantity
            if users.table_number:
                order_id.table_number=users.table_number
            if users.tip_amount:
                order_id.tip_amount=users.tip_amount
            order_id.order_type=mob_user.order_type
            order_id.save()
            users.order_id=order_id
            users.save()
            details.delete()
            Notification.objects.create(description=f"You Have New Order,Order ID {order_id.id}",receiver=user,sender=users.name,order_id=order_id.id)
            return render(request,'mobile_view/success_page.html',{'addtocart':addtocart,'user':user,'order_id':order_id.id})
            
        else:
            return redirect('mobile_home',id)
    def post(self,request,id):
        order_id=request.POST.get('order_id')
        review=request.POST.get('review')
        order=Order.objects.get(id=order_id)
        order.review=review
        order.save()
        return redirect('success-page',id)


# from django.db.models import Sum, Count, Avg
# def generate_order_pdf(request,id):
#     # Create a new PDF object
#     data=Order.objects.get(id=id)
#     user=UserDetails.objects.get(order_id=data)
#     order_details=Allorders.objects.filter(order_id=data)
#     all_tottal=order_details.aggregate(Sum('price'))['price__sum']
    
#     context=[]
#     for order in order_details:
#         addon=FoodAdd.objects.filter(order_id=order)
#         d={
#             'item_name':order.food_id.food_name,
#             'item_image':order.food_id.food_image,
#             'quanitity':order.quantity,
#             'total_price':int(order.price),
#             'price':order.food_id.price,
#         }
#         context.append(d)
#     template = get_template('mobile_view/order_details.html')
#     html = template.render({'data': data,'user':user,'context':context,'all_tottal':int(all_tottal),'addon':addon})

#     # Convert HTML to PDF
#     pdf_file = open('my_pdf_file.pdf', 'w+b')
#     pisa_status = pisa.CreatePDF(html.encode('utf-8'), dest=pdf_file)

#     # Return the PDF as a response
#     if pisa_status.err:
#         return HttpResponse('Error generating PDF file')
#     else:
#         pdf_file.seek(0)
#         response = HttpResponse(pdf_file, content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="my_order_receipt.pdf"'
#         return response
    


def get_states(request):
    country_id = request.GET.get('country_id')
    states = Region.objects.filter( Q(country_id=Country.objects.get(id=country_id))).order_by('name')
    state_list = list(states.values('id', 'name'))
    return JsonResponse({'states': state_list})

def get_cities(request):
    state_id = Region.objects.get(id=request.GET.get('state_id'))
    cities = City.objects.filter(region_id=state_id,country_id=state_id.country_id).order_by('name')
    city_list = list(cities.values('id', 'name'))
    return JsonResponse({'cities': city_list})



class Rating(View):
    def post(self,request):
        order_id=request.POST.get('order_id')
        rating=request.POST.get('rating')
        order=Order.objects.get(id=order_id)
        order.newrating = rating
        order.save()
        return JsonResponse({'msg':'Rated'})



class Change_Order_type(View):
    def post(self,request,id):
        order_type=request.POST.get('order_type')
        if not request.session.session_key:
            request.session.create()
        unique_id = request.session.get('unique_id', None)
        if not unique_id:
            unique_id = str(request.session.session_key)  # Use session ID as unique identifier
            request.session['unique_id'] = unique_id
        User_unique_id.objects.filter(unique_id=unique_id,user_id=CustomUser.objects.get(id=id)).update(order_type=order_type)
        return JsonResponse({'msg':'Changed'})

class User_Current_Location(View):
    def post(self,request):
        lat=request.POST.get('latitude')
        lon=request.POST.get('longitude')
        unique=request.POST.get('unique_id')
        user_id=request.POST.get('user_id')
        user=User_unique_id.objects.get(unique_id=unique,user_id=CustomUser.objects.get(id=user_id))
        user.latitude=lat
        user.longitude=lon
        user.save()
        return JsonResponse({'msg':'changed'})
    

class Search_meal(View):
    def post(self,request):
        search=request.POST.get('search')
        print(search)
        return redirect('mob_Item_details',search)
    




def download_html_template(request,id):
    # Your logic to generate or retrieve HTML content goes here
    data=Order.objects.get(id=id)
    user_details=UserDetails.objects.get(order_id=data)
    order_details=Allorders.objects.filter(order_id=data)
    
    users=CustomUser.objects.get(id=request.user.id)
    service_price=(users.service_fee * data.totalprice)/100
    total=service_price+data.totalprice
    qr_code = users.qr_code.path
    # Render HTML template as a string
    html_string = get_template('restaurent_admin/recipt.html').render({'users':users,'user_details':user_details,'order_details':order_details,'data':data,'total':total,'qr_code':qr_code,'service_price':service_price})
    # Create an HTTP response with the HTML content
    response = HttpResponse(html_string, content_type='text/html')

    # Set the Content-Disposition header to force download
    response['Content-Disposition'] = 'attachment; filename="login.html"'

    return response



def download_html_template(request,id):
    # Your logic to generate or retrieve HTML content goes here
    data=Order.objects.get(id=id)
    user_details=UserDetails.objects.get(order_id=data)
    order_details=Allorders.objects.filter(order_id=data)
    
    users=CustomUser.objects.get(id=request.user.id)
    service_price=(users.service_fee * data.totalprice)/100
    total=service_price+data.totalprice
    qr_code = users.qr_code
    return render(request,'restaurent_admin/recipt.html',{'users':users,'user_details':user_details,'order_details':order_details,'data':data,'total':total,'qr_code':qr_code,'service_price':service_price})
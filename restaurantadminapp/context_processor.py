from Adminapp.models import *
from restaurantadminapp.models import *
from datetime import datetime

def qrcodeshow(request):
    if CustomUser.objects.filter(id=request.user.id,is_superuser=False):
        qrimagecode=CustomUser.objects.get(id=request.user.id,is_superuser=False)
        notify1=Notification.objects.filter(receiver=qrimagecode,status='live').order_by('-id')
        noti=Notification.objects.filter(receiver=qrimagecode,read=False).count()
        today_date=datetime.now().date()
        print(today_date,'date')
        tranfer_date = datetime.strptime('2023-12-05','%Y-%m-%d')
        payment= OrderPayment.objects.filter(users_id=qrimagecode,order_transfer_date = today_date,status = 'Pending')
        if payment:
            transfer = True
        else:
            transfer = False
        print(transfer)
        return {'qrimagecode':qrimagecode,'notify1':notify1,'noticount':noti,'today_date':today_date,'transfer':transfer}
    else:
        qrimagecode='hello'
        return {'qrimagecode':qrimagecode}  
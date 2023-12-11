from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns=[
    path('admin-login/',views.login,name='admin-login'),
    path('admin-dashboard/',views.AdminDashboard.as_view(),name='admin-dashboard'),
    path('admin-logout/',views.Admin_logout,name='admin-logout'),
    path('change-password/',views.Change_password.as_view(),name='change-password'),
    path('forgot-password/',views.ForgotPassword.as_view(),name='forgot-password'),
################################   Users Show   ########################
    path('add-users/',views.Add_Users.as_view(),name='add-users'),
    path('edit-users/<int:id>',views.Edit_Users.as_view(),name='edit-users'),
    path('show-users/',views.Show_Users.as_view(),name='show-users'),
    path('delete-users/<int:id>',views.Delete_Users,name='delete-users'),
    path('show-profile/<int:id>',views.Show_Profile,name='show-profile'),
    path('active-inactive/',views.Active_inActive.as_view(),name='active-inactive'),
    path('edit-admin/',views.Edit_Admin.as_view(),name='edit-admin'),
    path('enable-disable/',views.Payment_enable_diable.as_view(),name='enable-disable'),
    path('Transaction-History/<int:id>',views.User_Transaction_history.as_view(),name='Tranaction_history'),
    path('Delete-Transaction-History/<int:id>',views.Delete_User_Transaction.as_view(),name='Delete_Tranaction_history'),
   
####################  Restaurants Show #################


    path('payament_details',views.User_Payment.as_view(),name='payament_details'),
    path('user-orders/<int:id>',views.User_Orders.as_view(),name='user_order'),
   

    

    path('add-subscription',views.Add_SubscriptionsDetails.as_view(),name='add-subscription'),
    path('show-subscription',views.Show_SubscriptionsDetails.as_view(),name='show-subscription'),
    path('edit-subscription/<int:id>',views.Edit_SubscriptionsDetails.as_view(),name='edit-subscription'),
    path('enable-disable-subcription/',views.enable_diable_subscription.as_view(),name='enable_diable_subscription'),
    path('Show-subcription-feature/<int:id>',views.Show_subscription_features.as_view(),name='show_subscription_feature'),
    path('Add-subcription-feature/<int:id>',views.Add_subscription_features.as_view(),name='add_subscription_features'),
    path('Edit-subcription-feature/<int:id>',views.Edit_subscription_features.as_view(),name='edit_subscription_features'),
    path('Delete-subcription-feature/<int:id>',views.Delete_Subscription_feature.as_view(),name='delete_subscription_features'),
    # path('delete-subscription/<int:id>',views.delete_subscriptionsdetails,name='delete-subscription'),


    path('sent-notification/',views.Add_Notifiactions.as_view(),name='sent-notification'),
    path('show-notification/',views.Notifiactions_show.as_view(),name='show-notification'),
    path('delete-notification/<int:id>',views.delete_notifications,name='delete-notification'),
    path('delete-all-notification/',views.delete_all_notifications,name='delete-all-notification'),
    path('404/', views.handler404, name='handler404'),





###term And condition

    path('add-termandcondition',views.Termsandconditions_add.as_view(),name='add-termandcondition'),
    path('show-termandcondition',views.Termsandconditions_show.as_view(),name='show-termandcondition'),
    path('edit-termandcondition/<int:id>',views.Termsandconditions_Edit.as_view(),name='edit-termandcondition'),
    path('delete-termandcondition/<int:id>',views.delete_Termsandconditions,name='delete-termandcondition'),


####Privacy and Policy
    path('add-privacyandpolicy',views.Privacyandpolicy_add.as_view(),name='add-privacyandpolicy'),
    path('show-privacyandpolicy',views.Privacyandpolicy_show.as_view(),name='show-privacyandpolicy'),
    path('edit-privacyandpolicy/<int:id>',views.Privacyandpolicy_Edit.as_view(),name='edit-privacyandpolicy'),
    path('delete-privacyandpolicy/<int:id>',views.delete_Privacyandpolicy,name='delete-privacyandpolicy'),

##############Show Menu

    path('menu-details/<int:id>',views.Show_Menu_Categories.as_view(),name='menu-details'),
    path('edit-menu-details/<int:id>',views.Edit_Menu_Categories.as_view(),name='edit-menu-details'),
    path('delete-menu-details/<int:id>',views.delete_category,name='delete-menu-details'),



    path('show-menu-food/<int:id>',views.Show_Menu_food_items.as_view(),name='show-menu-food'),
    path('edit-menu-food/<int:id>',views.Edit_Menu_food_items.as_view(),name='edit-menu-food'),
    path('delete-menu-food/<int:id>',views.delete_item,name='delete-menu-food'),


    path('add-image/',views.Add_Category_Image.as_view(),name='add-image'),
    path('Show-Image',views.Show_Category_Image.as_view(),name='show-image'),
    path('edit-image/<int:id>',views.Edid_Category_Image.as_view(),name='edit-image'),
    path('delete-image/<int:id>',views.deleteimage,name='delete-image'),




    path('show-suggestion',views.Show_food_suggestions.as_view(),name='show_suggestion'),
    path('add-suggestion',views.Add_food_suggestions.as_view(),name='add_suggestion'),


]







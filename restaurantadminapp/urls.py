from django.urls import path ,include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns=[

    path('',views.User_Login.as_view(),name='user-login'),
    path('user-registration/',views.UserRegistration.as_view(),name='user-registration'),
    path('user-dashboard/',views.UserDashboard.as_view(),name='user-dashboard'),
    path('change-user-password/',views.Change_password.as_view(),name='change-user-password'),
    # path('edit-user-profile/<int:id>',views.Edit_Users_Profile.as_view(),name='edit-users-profile'),
    # path('add-restaurant-details/',views.Add_Restaurant_Deltails.as_view(),name='add-restaurant-details'),
    path('Receive_notifiaction_count/',views.Check_new_notification.as_view()),
    path('download-html/<int:id>', views.download_html_template, name='download_html_template'),
    
    path('restaurant-details/',views.Restaurant_details.as_view(),name='restaurant-details'),
    path('connect/',views.ConnectWithStripe.as_view(),name='connect'),
    path('Account-status/<str:id>',views.Account_status.as_view(),name='account_status'),
    path('remove-banner/',views.Remove_banner.as_view(),name='remove-banner'),
    path('Delete-Profile/',views.DeleteImage.as_view(),name='deleteImage'),
    path('account-detail/',views.Account_Detail.as_view(),name='account_detail'),
    path('subscription/',views.User_Subscription.as_view(),name='subscription'),
    path('Payment/',views.Payment.as_view(),name='Payment'),
    path('user-logout/',views.userlogout,name='user-logout'),
    # path('user-forgot-password/',views.Forget_password.as_view(),name='user-forgot-password'),
    path('Transaction-History/',views.Transaction_History.as_view(),name='t_history'),
    path('Delete-Transaction-History/',views.Delete_Transaction_History.as_view(),name='delete_t_history'),
    path('Edit-Stripe-Account/',views.Edit_stripe_account.as_view(),name='edit_details_accounts'),
    

#############################Categorties######################
    path('add-category/',views.Add_Category.as_view(),name='add-category'),
    path('show-category/',views.Show_Category.as_view(),name='show-category'),
    path('edit-category/',views.Edit_Category.as_view(),name='edit-category'),
    path('delete-category/',views.delete_category,name='delete-category'),
    path('show-category-image/',views.Show_cat_image.as_view()),
    path('category-details/',views.caterogy_details.as_view()),


############################Add Food item #################
    path('add-item/<int:id>',views.Add_Item.as_view(),name='add-item'),
    path('add-once/<int:id>',views.Add_Once.as_view(),name='add-once'),
    path('delete-add-once/<int:id>',views.Delete_Add_Once.as_view(),name='delete-add-once'),
    path('show-item/<int:id>',views.Show_Item.as_view(),name='show-item'),
    path('edit-item/<int:id>',views.Edit_Item.as_view(),name='edit-item'),
    path('delete-item/',views.Delete_item.as_view(),name='delete-item'),
    path('show-all-item/<int:cat_ids>',views.Show_all_items.as_view(),name='show-all-item'),
    path('show-all-Draft-item/<int:cat_ids>',views.Show_all_draft_items.as_view(),name='show-all-draft-item'),
    path('add-items/',views.Add_Item_all.as_view(),name='add-all-item'),
    path('change-status/<int:id>',views.Change_Item_status.as_view()),
    path('add-ons-group/',views.Adons_group.as_view()),
    path('deleteGroup/<int:id>',views.Delete_Groups.as_view()),
    # path('all-data/<int:id>',views.all_addons_show.as_view()),


    path('Order-History/',views.Order_history.as_view(),name='order_history'),
    path('complete-order/',views.Completeorder.as_view(),name='Completeorder'),
    path('custom-image-category/',views.Custom_catgory_images.as_view(),name='customcatimage'),
    path('delete-custom-category/',views.Delete_custom_images.as_view(),name='deletecustomcatimage'),

    path('get_states/', views.get_states, name='get_states'),
    path('get_cities/', views.get_cities, name='get_cities'),
    path('send-sms/<int:id>', views.send_sms, name='send_sms'),
    path('rating/',views.Rating.as_view()),
    path('table_status/',views.Table_status.as_view()),

    # path('menu/<str:id>',views.Restaurant_Menu.as_view(),name='restaurant-menu'),
    # path('food-item/<int:id>',views.Food_Items.as_view(),name='food-item')



    path('receive-Transfer_amount/',views.Transfer_amount.as_view(),name='receive-Transfer_amount'),  
    path('receive-notification/',views.Receive_Notification.as_view(),name='receive-notification'),  
    path('change-notification-status/',views.Change_notification_status,name='change-notification-status'),  
    path('delete-receive-notification/<int:id>',views.delete_notification,name='delete-receive-notification'),
    path('remove-receive-notification/<int:id>',views.Remove_notification.as_view(),name='remove-receive-notification'),
    path('notification-details/<int:id>',views.Notification_details.as_view(),name='notification-details'),



    path('generate-pdf/<int:id>', views.generate_pdf, name='generate-pdf'),
    path('TermandConditions', views.TermandConditions.as_view(), name='TermandConditions'),
    path('Privacyandpolicies', views.Privacyandpolicies.as_view(), name='privacyandpolicies'),

    path('password_reset/',auth_views.PasswordResetView.as_view(template_name='restaurent_admin/password_reset.html'),name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='restaurent_admin/password_reset_done.html'),name='password_reset_done'),
    # path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='restaurent_admin\password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='restaurent_admin/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',auth_views.PasswordResetCompleteView.as_view(template_name='restaurent_admin/password_reset_complete.html'),name='password_reset_complete'),



#####mobile View ####
    path('mobile-home/<int:id>',views.Mobile_home.as_view(),name='mobile_home'),
    path('mobile-items/<int:id>',views.Mobile_items.as_view(),name='mobile_items'),
    # path('add-to-cart/<int:id>',views.Addtocarts.as_view(),name='Addtocarts'),
    path('add-to-cart-view/<int:id>',views.AddToCartView.as_view(),name='AddToCartView'),
    path('add-to-cart-remove/<int:id>',views.RemoveAddtocart.as_view(),name='RemoveAddtocart'),
    path('item-details/<int:id>',views.Mob_Item_details.as_view(),name='mob_Item_details'),
    path('Manage-quantity/',views.ManageQuantity.as_view(),name='manageQuantity'),
    # path('Check-Out/<int:id>',views.Checkout.as_view(),name='checkout'),
    path('checkout/<int:id>',views.CheckOutSession.as_view(),name='checkout_page'),
    path('Success-Page/<int:id>',views.SuccessPage.as_view(),name='success-page'),
    path('Change-Order-Type/<int:id>',views.Change_Order_type.as_view()),
    path('user-location/',views.User_Current_Location.as_view()),
    path('search-meal/',views.Search_meal.as_view(),name='search_meal'),
    # path('Order_details/<int:id>',views.generate_order_pdf,name='order-Details'),



]   
from django.urls import path
from .views import *
urlpatterns=[
    path('',home,name='home'),
    path('add/',Add_account,name='add'),
    path('deposit/', deposit, name='deposit'),
    path('withdraw/', withdraw, name='withdraw'),
    path('balance/', check_balance, name='balance'),
    path('admin_login/',admin_login, name='admin_login'),
    path('admin_page/',admin_page, name='admin_page'),
    path('logout/',logout_view, name='logout'),
    path('show_account/',show_account, name='show_account'),
    path('updatepage/<int:id>/',updatepage, name='updatepage'),
    path('deletepage/<int:id>/',deletepage, name='deletepage'),
    
]




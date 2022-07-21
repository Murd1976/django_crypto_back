from django.urls import include, path, re_path
from crypto_back import views
from .views import BBLoginView, BBLogoutView

app_name = 'crypto_back'
urlpatterns = [
#    path('accounts/register/done/', views.RegisterDoneView.as_view(), name= 'my_register_done'),
#    path('accounts/register/', views.RegisterUserView.as_view(), name= 'my_register'),
    path('accounts/profile/change/', views.ChangeUserInfoView.as_view(), name= 'my_profile_change'),
    path('accounts/profile/', views.user_profile, name= 'my_profile'),
    path('accounts/login/', BBLoginView.as_view(), name= 'my_login'),
    path('accounts/logout/', BBLogoutView.as_view(), name= 'my_logout'),
    path('accounts/password/change/', views.BBPasswordChangeView.as_view(), name= 'my_password_change'),
    path('<str:page>/', views.other_page, name= 'other'),
    path('', views.index, name='index'),
    path('m400', views.m400),
    path('home/', views.home),
#    re_path(r'^about', views.about),
    re_path(r'^contact', views.contact),
    
    path('products/', views.products),
    path('products/<int:productid>/', views.products),
     
    path('users/', views.users),
    path('users/<int:id>/<str:name>/', views.users),
     
]



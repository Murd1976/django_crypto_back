from django.urls import include, path, re_path
from crypto_back import views
from .views import BBLoginView, BBLogoutView

app_name = 'crypto_back'
urlpatterns = [
    path('', views.index, name='index'),
    
    path('accounts/register/activate/<str:sign>/', views.user_activate, name= 'my_register_activate'),
    path('accounts/register/done/', views.RegisterDoneView.as_view(), name= 'my_register_done'),
    path('accounts/register/', views.RegisterUserView.as_view(), name= 'my_register'),
    path('accounts/profile/delete/', views.DeleteUserView.as_view(), name= 'my_profile_delete'),
    path('accounts/profile/change/', views.ChangeUserInfoView.as_view(), name= 'my_profile_change'),
    path('back_test/', views.run_test_page, name='my_backtest'),
    path('strategy/', views.choise_strategy_page, name='my_choise_strategy'),
    path('reports/', views.create_report_page, name='my_create_report'),
    path('reports/txt/', views.reports_txt_files_list, name='my_txt_reports'),
    path('reports/txt/delete/<str:f_name>/', views.delete_txt_report, name='my_delete_txt_reports'),
    path('reports/xlsx/', views.reports_xlsx_files_list, name='my_xlsx_reports'),
    path('reports/xlsx/delete/<str:f_name>/', views.delete_xlsx_report, name='my_delete_xlsx_reports'),
    re_path(r'^download/$', views.download_report),
    path('tests/', views.tests_list_page, name= 'my_tests_list'),
    path('tests/delete/<int:id>/', views.delete_tests, name= 'my_delete_tests'),
    path('accounts/profile/', views.user_profile, name= 'my_profile'),
    path('accounts/login/', BBLoginView.as_view(), name= 'my_login'),
    path('accounts/logout/', BBLogoutView.as_view(), name= 'my_logout'),
    path('accounts/password/change/', views.BBPasswordChangeView.as_view(), name= 'my_password_change'),
    path('<str:page>/', views.other_page, name= 'other'),
#    path('crypto_templ/', views.other_page, name= 'other'),
    
    path('m400', views.m400),
    path('home/', views.home),
#    re_path(r'^about', views.about),
#    re_path(r'^<str:page>/', views.other_page, name= 'other'),
    re_path(r'^contact', views.contact),
    
    path('products/', views.products),
    path('products/<int:productid>/', views.products),
     
    path('users/', views.users),
    path('users/<int:id>/<str:name>/', views.users),
     
]



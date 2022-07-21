from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.base import TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404

#from .forms import UserForm
from .models import AdvUser
from .forms import ChangeUserInfoForm #, RegisterUserForm

class BBLoginView(LoginView):
    template_name = 'crypto_templ/cr_login.html'
    
class BBLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'crypto_templ/cr_logout.html'

#class RegisterDoneView(TemplateView):
#    template_name = 'crypto_templ/cr_register_done.html'
    
#class RegisterUserView(CreateView):
#    model = AdvUser
#    template_name = 'crypto_templ/cr_register_user.html'
#    form_class = RegisterUserForm
#    success_url = reverse_lazy('crypto_back:register_done')
    
class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'crypto_templ/cr_change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('crypto_back:profile')
    success_message = 'User data changed'
    
    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)
    
class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'crypto_templ/cr_password_change.html'
    success_url = reverse_lazy('crypto_back:profile')
    success_message = 'User password changed'
    
def index(request):    
    return render(request, "crypto_templ/index.html")

@login_required
def user_profile(request):
    return render(request, 'crypto_templ/cr_profile.html')

#def index(request):
#    if request.method == "POST":
#        name = request.POST.get("name")
#        age = request.POST.get("age")     # получение значения поля age
#        checked1 = request.POST.get("check1")
#        return HttpResponse("<h2>Hello, {0} Checked: {1}</h2>".format(name, checked1))
#    else:
#        userform = UserForm()
#    return render(request, "index.html", {"form": userform})

def other_page(request, page):
    try:
        template = get_template('crypto_templ/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request = request))

def home(request):
    data = {"header": "Main window", "message": "Welcome to Crypto-backtest!"}
    return render(request, "crypto_templ/home.html", context=data)
 
#def about(request):
#    header = "Personal Data"                    # обычная переменная
#    langs = ["English", "German", "Spanish"]    # массив
#    user ={"name" : "Tom", "age" : 23}          # словарь
#    addr = ("Абрикосовая", 23, 45)              # кортеж
 
#    data = {"header": header, "langs": langs, "user": user, "address": addr}
#    return render(request, "crypto_templ/pers_data.html", context=data)
 
def contact(request):
    return HttpResponse("<h2>Контакты</h2>")

def products(request, productid=17):
    category = request.GET.get("cat", "")
    output = "<h2>Product № {0}  Category: {1}</h2>".format(productid, category)
    return HttpResponse(output)
 
def users(request):
    id = request.GET.get("id", 1)
    name = request.GET.get("name", "Den")
    output = "<h2>User</h2><h3>id: {0}  name: {1}</h3>".format(id, name)
    return HttpResponse(output)

def m304(request):
    return HttpResponseNotModified()
 
def m400(request):
    return HttpResponseBadRequest("<h2>Bad Request</h2>")
 
def m403(request):
    return HttpResponseForbidden("<h2>Forbidden</h2>")
 
def m404(request):
    return HttpResponseNotFound("<h2>Not Found</h2>")
 
def m405(request):
    return HttpResponseNotAllowed("<h2>Method is not allowed</h2>")
 
def m410(request):
    return HttpResponseGone("<h2>Content is no longer here</h2>")
 
def m500(request):
    return HttpResponseServerError("<h2>Something is wrong</h2>")





from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseBadRequest, Http404
from django.shortcuts import render, redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.core.signing import BadSignature
from django.utils.encoding import smart_str
import os
import mimetypes

from .forms import *
from .models import AdvUser, AllBackTests, DataBufer
#from .forms import ChangeUserInfoForm, RegisterUserForm
from .utilities import signer
from .main_web import ExampleApp
from .strategies_list import Available_strategies


class BBLoginView(LoginView):
    template_name = 'crypto_templ/cr_login.html'
    
class BBLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'crypto_templ/cr_logout.html'

class RegisterDoneView(TemplateView):
    template_name = 'crypto_templ/cr_register_done.html'
    
class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'crypto_templ/cr_register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('crypto_back:my_register_done')

class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'crypto_templ/cr_change_user_info.html'
    form_class = ChangeUserInfoForm
    success_url = reverse_lazy('crypto_back:my_profile')
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
    success_url = reverse_lazy('crypto_back:my_profile')
    success_message = 'User password changed'
    
class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'crypto_templ/cr_delete_user.html'
    success_url = reverse_lazy('crypto_back:index')
    
    def setup(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().setup(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'User deleted')
        return super().post(request, *args, **kwargs)
    
    def get_object(self, queryset = None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk = self.user_id)
    
def index(request):    
    return render(request, "crypto_templ/index.html")

@login_required
def user_profile(request):
    return render(request, 'crypto_templ/cr_profile.html')

def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'crypto_templ/cr_bad_signature.html')
    
    user = get_object_or_404(AdvUser, username = username)
    if user.is_activated:
        template = 'crypto_templ/cr_user_is_activated.html'
    else:
        template = 'crypto_templ/cr_activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)

#def index(request):
#    if request.method == "POST":
#        name = request.POST.get("name")
#        age = request.POST.get("age")     # получение значения поля age
#        checked1 = request.POST.get("check1")
#        return HttpResponse("<h2>Hello, {0} Checked: {1}</h2>".format(name, checked1))
#    else:
#        userform = UserForm()
#    return render(request, "index.html", {"form": userform})

@login_required
def test_mod_form(request):
#    if request.method == "POST":
#        userform = TestBackTestForm(request.POST or None)
#        if userform.is_valid():
#            bb = userform.save()
#            return redirect('crypto_back:index')
#        
    template = 'crypto_templ/cr_test_model.html'
    parts = TestBackTestForm(initial={'owner':request.user.pk})
    context = {"form": parts}
    return render(request, template, context)

@login_required
def tests_list_page(request):
#    if request.method == "POST":
#        userform = TestBackTestForm(request.POST or None)
#        if userform.is_valid():
#            bb = userform.save()
#            return redirect('crypto_back:index')
#        
    template = 'crypto_templ/cr_tests_list.html'
    tests_list = AllBackTests.objects.filter(owner=request.user)
#    tests_list = AllBackTests.objects.all()
    context = {"tests_list": tests_list, "user_name":request.user}
    return render(request, template, context)

# delete record of tests
def delete_tests(request, id):
    try:
        test = AllBackTests.objects.get(id=id)
        test.delete()
        return redirect('crypto_back:my_tests_list')
    except AllBackTests.DoesNotExist:
        return HttpResponseNotFound("<h2>Record not found</h2>")

@login_required
def choise_strategy_page(request):
    template = 'crypto_templ/cr_choise_strategy.html'
#    ui_utils = ExampleApp()
#    strategies_val, reports_val = ui_utils.connect_ssh()
#    strategies_index = []
#    reports_index = []
#    if len(strategies_val) > 0:
#	    for b in range(len(strategies_val)):
#	        strategies_index.append(str(b))
            
#    if len(reports_val) > 0:
#	    for b in range(len(reports_val)):
#	        reports_index.append(str(b))

#    strategies_list = list(zip(strategies_index, strategies_val))
#    reports_list = list(zip(reports_index, reports_val))

    strategies_list = Available_strategies.strategies_names_tuple
    
    if request.method == "POST":
        text_buf = "Name of strategy: "
        userform = ChoiseStrategyForm(request.POST or None)
        text_buf += dict(strategies_value)[str(userform.data.get("f_strategies"))]
        
        
        if userform.is_valid():
            strategy_choise = userform.cleaned_data["f_strategies"]
            data_bufer = DataBufer.objects.filter(name=request.user)
            data_bufer.delete()
            
            data_bufer = DataBufer(name=request.user, user_strategy_choise=strategy_choise)
            data_bufer.save()
#            return reverse_lazy('crypto_back:my_backtest')
            return redirect('crypto_back:my_backtest')
#            return HttpResponse("<h2>Your choise: {0}  </h2>".format(user_strategy_choise))
        else:
            return HttpResponse(text_buf)
    
    
#    parts = ChoiseStrategyForm()
    parts = ChoiseStrategyForm(initial= {"f_text_log":strategies_list}) #{"f_strategies":strategies_val[0]})
    parts.fields['f_strategies'].choices = strategies_list
    context = {"form": parts}
    return render(request, template, context)

@login_required
def run_test_page(request):
    ui_utils = ExampleApp()
    ui_utils.server_user_directory = str(request.user)
    strategies_val, reports_val = ui_utils.connect_ssh()
#    strategies_index = []
    reports_index = []
#    if len(strategies_val) > 0:
#	    for b in range(len(strategies_val)):
#	        strategies_index.append(str(b))
            
    if len(reports_val) > 0:
	    for b in range(len(reports_val)):
	        reports_index.append(str(b))
            
#    strategies_list = list(zip(strategies_index, strategies_val))
    reports_list = list(zip(reports_index, reports_val))

    strategies_list = Available_strategies.strategies_names_tuple
    strategies_files = Available_strategies.strategies_file_tuple

    template = 'crypto_templ/cr_run_test.html'
    strategy_keys = ['f_strategies', 'f_reports', 'f_parts', 'f_series_len', 'f_price_inc', 'f_persent_same', 'f_min_roi_time1', 'f_min_roi_value1', 'f_min_roi_time2', 'f_min_roi_value2',
                         'f_min_roi_time3', 'f_min_roi_value3', 'f_min_roi_time4', 'f_min_roi_value4', 'f_movement_roi', 'f_des_stop_loss', 'f_stop_loss', 'f_my_stop_loss_time', 'f_my_stop_loss_value',
                         'f_text_log']
    p = []

    data_bufer = DataBufer.objects.filter(name=request.user)
    data_str = str(data_bufer[0])
    user_strategy_choise = data_str.split(':')[1]

    p.append(dict(strategies_files)[user_strategy_choise])
    
#    strategies_value = []
    if request.method == "POST":
        text_buf = "Name of strategy: "
        userform = BackTestForm(request.POST or None)
       
        if userform.is_valid():
            
            back_test_model = AllBackTests.objects.all()
#            text_buf += dict(strategies_list)[userform.cleaned_data["f_strategies"]]
#            text_buf = "Name of strategy: " + dict(strategies_value)[str(userform.data.get("f_strategies"))]
            
#            p.append(dict(strategies_list)[userform.cleaned_data["f_strategies"]])
            
#            p.append(dict(reports_list)[userform.cleaned_data["f_reports"]])
            p.append('no reports')
            
            p.append(userform.cleaned_data["f_parts"])
            p.append(userform.cleaned_data["f_series_len"])
            p.append(userform.cleaned_data["f_price_inc"])
            p.append(userform.cleaned_data["f_persent_same"])
                        
            p.append(userform.cleaned_data["f_min_roi_time1"])
            p.append(userform.cleaned_data["f_min_roi_value1"])
            p.append(userform.cleaned_data["f_min_roi_time2"])
            p.append(userform.cleaned_data["f_min_roi_value2"])
            p.append(userform.cleaned_data["f_min_roi_time3"])
            p.append(userform.cleaned_data["f_min_roi_value3"])
            p.append(userform.cleaned_data["f_min_roi_time4"])
            p.append(userform.cleaned_data["f_min_roi_value4"])
            
            p.append(userform.cleaned_data["f_movement_roi"])
            p.append(userform.cleaned_data["f_des_stop_loss"])
            p.append(userform.cleaned_data["f_stop_loss"])
            p.append(userform.cleaned_data["f_my_stop_loss_time"])
            p.append(userform.cleaned_data["f_my_stop_loss_value"])
            p.append(userform.cleaned_data["f_text_log"])
            
            p.append(request.user)
            
            
            back_test_record = AllBackTests(strategy_name= p[0], owner= p[20], parts= p[2], minimal_roi1_time= p[6], minimal_roi1_value= p[7], minimal_roi2_time= p[8], minimal_roi2_value= p[9], 
                                            minimal_roi3_time= p[10], minimal_roi3_value= p[11], minimal_roi4_time= p[12], minimal_roi4_value= p[13], arg_N= p[3], arg_R= p[4], arg_P= p[5], arg_MR= p[14],
                                            stoploss= p[16], my_stoploss_time= p[17], my_stoploss_value= p[18], arg_stoploss= p[15], text_log= p[19])
            back_test_record.save()

            strategy_settings = dict(list(zip(strategy_keys, p)))
            name=str(request.user)
            ui_utils.run_backtest(strategy_settings, name)
            strategy_settings['f_strategies'] = dict(strategies_list)[user_strategy_choise]
            strategy_settings["f_text_log"] = str(request.user) + '/ ' + str(ui_utils.list_info)
#            parts = BackTestForm(initial={"f_text_log":str(request.user) + '/ ' + str(ui_utils.list_info)})
            parts = BackTestForm(initial= strategy_settings)

            parts.fields['f_reports'].choices = reports_list		
            context = {"form": parts}
            return render(request, template, context)
#            return HttpResponse("<h2>Hello, {0} :{1} :{2} </h2>".format(text_buf, strategies_list[1], nnn))
        else:
            return HttpResponse("Invalid data")

    
    parts = BackTestForm()
    text_buf = str(ui_utils.list_info)
#    p.append( "min_roi_trailing_loss_4_4.py")
#    p.append(dict(strategies_files)[user_strategy_choise])
    for b in range(11):
        p.append('')
    strategy_settings = dict(list(zip(strategy_keys, p)))
    strategy_settings = ui_utils.param_of_cur_strategy(strategy_settings)
    strategy_settings['f_strategies'] = dict(strategies_list)[user_strategy_choise]
#    strategy_settings["f_text_log"] = strategy_settings
    parts = BackTestForm(initial= strategy_settings) #{"f_text_log":strategy_settings}) #text_buf})

#    parts = BackTestForm(initial= {"f_text_log":p[0]}) #text_buf})

    parts.fields['f_reports'].choices = reports_list

    context = {"form": parts}
    return render(request, template, context)

@login_required
def create_report_page(request):
    template = 'crypto_templ/cr_create_report.html'
    ui_utils = ExampleApp()
    ui_utils.server_user_directory = str(request.user)
    strategies_val, reports_val = ui_utils.connect_ssh()

    reports_index = []
            
    if len(reports_val) > 0:
	    for b in range(len(reports_val)):
	        reports_index.append(str(b))
	        
    reports_list = list(zip(reports_index, reports_val))

    if request.method == "POST":
        userform = CreateReportForm(reports_list, request.POST or None)
                
        if userform.is_valid():
            text_buf = dict(reports_list)[str(userform.cleaned_data["f_reports"])]
            name=str(request.user)
            ui_utils.run_report(text_buf, 'local', name)
            parts = CreateReportForm(reports_list, initial= {"f_text_log":str(ui_utils.list_info)})
#            parts.fields['f_reports'].choices = reports_list		
            context = {"form": parts}
            return render(request, template, context)
        
    parts = CreateReportForm(reports_list, initial= {"f_text_log":str(ui_utils.list_info)})    
#    parts = CreateReportForm(dynamic_choices = dict(reports_list))
#    parts.fields['f_reports'].choices = reports_list

    context = {"form": parts}
    return render(request, template, context)

@login_required
def reports_txt_files_list(request):
    name=str(request.user)
    f_path = './reports/' + name + '/txt/'

    if not os.path.exists('./reports/' + name):
        os.mkdir('./reports/' + name)
        os.mkdir(f_path)
    if not os.path.exists(f_path):
        os.mkdir(f_path)
        
    f_list = os.listdir('./reports/' + name + '/txt/')   
    
    return render(request, 'crypto_templ/cr_files_list.html', context = {'user_name':name, 'total_files':f_list, 'path':f_path})

@login_required
def delete_txt_report(request, f_name):
    name=str(request.user)
    f_path = './reports/' + name + '/txt/' + f_name
    if os.path.exists(f_path):
        os.remove(f_path)
    
    return redirect('crypto_back:my_txt_reports')

@login_required
def reports_xlsx_files_list(request):
    name=str(request.user)
    f_path = './reports/' + name + '/xlsx/'
    if not os.path.exists('./reports/' + name):
        os.mkdir('./reports/' + name)
        os.mkdir(f_path)
    if not os.path.exists(f_path):
        os.mkdir(f_path)
        
    f_list = os.listdir('./reports/' + name + '/xlsx/')
    
    return render(request, 'crypto_templ/cr_files_list.html', context = {'user_name':name, 'total_files':f_list, 'path':f_path})

@login_required
def delete_xlsx_report(request, f_name):
    name=str(request.user)
    f_path = './reports/' + name + '/xlsx/' + f_name
    if os.path.exists(f_path):
        os.remove(f_path)
    
    return redirect('crypto_back:my_xlsx_reports')

@login_required
def download_report(request):
    # Get the filename
    file_name = request.GET.get('file_name')
    if file_name != '':
        user_name=str(request.user)
        st = file_name.split('.')
        path_to_file = ''
        if st[1] == 'txt':
            # Define the full file path
            path_to_file = "./reports/{0}/txt/{1}".format(user_name, file_name)
        if st[1] == 'xlsx':
            # Define the full file path
            path_to_file = "./reports/{0}/xlsx/{1}".format(user_name, file_name)
        if path_to_file == '':
           return render(request, 'crypto_templ/cr_files_list.html') 
            
        # Open the file for reading content
        f = open(path_to_file, 'rb')
        # Set the mime type
        mime_type, _ = mimetypes.guess_type(path_to_file)
        # Set the return value of the HttpResponse
        response = HttpResponse(f, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name
#       response['X-Sendfile'] = smart_str(path_to_file)
        return response
    else:
        # Load the template
        return render(request, 'crypto_templ/cr_files_list.html')


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






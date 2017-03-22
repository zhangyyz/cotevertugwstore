# >>>>>>>>>>For Testing: Delete me>>>>>>>>>>
"""
import base64
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from PIL import Image
import urllib
from io import BytesIO
from .models import Barcode

def download_bar_code(request):
    for i in range(9990000001, 9990000500):
        url = "http://www.fastontime.com/cgi-bin/GInfo.dll?BarCode&ccode={0}&ih=85&iw=265&ntype=0".format(i)
        img = Image.open(BytesIO(urllib.request.urlopen(url).read()))
        imgbuf = BytesIO()
        img.save(imgbuf, format='PNG')
        base64str ='data:image/png;base64,' + str(base64.b64encode(imgbuf.getvalue()))[2:-1]
        barcode = Barcode()
        barcode.number = i
        barcode.image_data_uri = base64str
        barcode.save()
    return HttpResponse('success')
"""
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<
import decimal
import mimetypes
import os
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import render
from .forms import BillForm
from .forms import UserForm
from .models import Bill
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .my_tools import generate_bill_number
from .my_tools import save_batch_pdf_and_send_email
from .my_tools import save_barcodes_to_pdf
from .my_tools import save_batch_bills_to_one_pdf
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from .models import HTMLCode
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
import datetime
import uuid
from django.conf import settings

MY_BATCH_BILLS_SAVING_PATH_FOR_SUBMITTING_TO_FASTONTIME = settings.MY_BATCH_BILLS_SAVING_PATH_FOR_SUBMITTING_TO_FASTONTIME

def is_admin(user):
    return user.is_superuser

def reset_password(request):
    if request.method == 'GET':
        return render(request, 'gwstore/resetpassword.html')
    if request.method == 'POST':
        users = User.objects.filter(email__iexact=request.POST['email'])
        if len(users) == 0:
            return JsonResponse({"status": "failed", "error": u"系统中没有查询到您所提交的Email。"})
        user = users[0]
        new_password = str(uuid.uuid4())[-6:]
        user.set_password(new_password) #Password has been changed
        user.save()

        #Send the new password to the user by email
        message = EmailMessage(
        subject='您的密码已经被重置 -- 联通快递Cote Vertu收货点',
        body=u"""
您好,

您在http://www.cotevertu.com的用户名为： {0}

您的密码已经被重置为： {1}

请使用上述的新密码登录，然后再把密码修改为一个容易记住的密码。

谢谢您的支持！
""".format(user.username, new_password),
        from_email='fastontimecotevertu@gmail.com',
        to=[user.email])
        message.send()
        return JsonResponse({"status": "success"})


@user_passes_test(is_admin)
def batch_download_barcodes(request):
    bill_numbers = request.GET['bill_numbers_batch'].split(",")
    generated_pdf_path = save_barcodes_to_pdf(bill_numbers)
    filename = os.path.basename(generated_pdf_path)
    response = FileResponse(open(generated_pdf_path, 'rb'),
                            content_type=mimetypes.guess_type(generated_pdf_path)[0])
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


@user_passes_test(is_admin)
def batch_download_bills_pdf(request):
    bill_numbers = request.GET['bill_numbers_batch'].split(",")
    now = datetime.datetime.now()
    generated_pdf_path = save_batch_bills_to_one_pdf(bill_numbers,
                                                     save_to_directory=MY_BATCH_BILLS_SAVING_PATH_FOR_SUBMITTING_TO_FASTONTIME.format(
                                                         now.strftime('%Y%m%d')),
                                                     filename=str(uuid.uuid4()) +".pdf")
    filename = os.path.basename(generated_pdf_path)
    response = FileResponse(open(generated_pdf_path, 'rb'),
                            content_type=mimetypes.guess_type(generated_pdf_path)[0])
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


@user_passes_test(is_admin)
def batch_download_bills_excel(request):
    import csv
    from django.utils.encoding import smart_str

    bill_numbers = request.GET['bill_numbers_batch'].split(",")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(smart_str('BatchDownloadedBills.csv'))
    response.write(u'\ufeff'.encode('utf8'))  # Put BOM in the head of the file so that Excel can read it correctly.
    writer = csv.writer(response, dialect='excel')
    writer.writerow([u'备注', u'发件人账号', u'单号', u'发件人', u'发件电话', u'收件人', u'收件电话', u'收件地址', u'物品描述', u'重量'])
    all_bills = Bill.objects.filter(bill_number__in=bill_numbers)
    for bill in all_bills:
        insurance_desc = ""
        if bill.package_lost_insured_amount > 0:
            insurance_desc = u"保${0}加币".format(bill.package_lost_insured_amount)
        else:
            insurance_desc = ""
        item_list = bill.item_1_description + "*" + str(bill.item_1_quantity)
        if bill.item_2_description != '':
            item_list += u"，" + bill.item_2_description + "*" + str(bill.item_2_quantity or '')
        if bill.item_3_description != '':
            item_list += u"，" + bill.item_3_description + "*" + str(bill.item_3_quantity or '')
        if bill.item_4_description != '':
            item_list += u"，" + bill.item_4_description + "*" + str(bill.item_4_quantity or '')
        if bill.item_5_description != '':
            item_list += u"，" + bill.item_5_description + "*" + str(bill.item_5_quantity or '')
        if bill.pickup_person.first_name == u'郭武':
            fastontime_member_name = "MGUOWU"
        else:
            fastontime_member_name = "MWJN"

        writer.writerow([insurance_desc, fastontime_member_name, bill.bill_number, bill.sender_name, bill.sender_phone,
                         bill.receiver_name, bill.receiver_phone, bill.receiver_address, item_list, bill.weight_lb])
        # Mark the excel exported time for the bill
        bill.batch_excel_exported_time = timezone.now()
        bill.save()
    return response

@user_passes_test(is_admin)
def no_bill_exported_before(request):
    bill_numbers = request.GET['bill_numbers_batch'].split(",")
    bills_already_exported = Bill.objects.filter(bill_number__in=bill_numbers, batch_excel_exported_time__isnull = False )
    if len(bills_already_exported) > 0:
        exported_bill_numbers = ""
        for bill in bills_already_exported:
            exported_bill_numbers += str(bill.bill_number) + ", "
        exported_bill_numbers = exported_bill_numbers[:-2] #Strip the comma and space from the end of the string.
        return JsonResponse({'status': 'failed', 'bill_numbers': exported_bill_numbers})
    else:
        return JsonResponse({'status': 'success'})

@user_passes_test(is_admin)
def admin_collect_info(request):
    if request.method == 'GET':
        filters = []
        if request.GET.get('from_pickup_date_to_search', '') != '':
            filters.append(Q(
                pickup_time__gte=datetime.datetime.strptime(request.GET.get('from_pickup_date_to_search', '').strip(),
                                                            "%Y-%m-%d")))
        if request.GET.get('to_pickup_date_to_search', '') != '':
            filters.append(
                Q(pickup_time__lt=datetime.datetime.strptime(request.GET.get('to_pickup_date_to_search', '').strip(),
                                                             "%Y-%m-%d") + datetime.timedelta(days=1)))
        if request.GET.get('status_code_to_search', '') != '':
            filters.append(Q(status_code=request.GET['status_code_to_search']))
        if request.GET.get('pickup_person_to_search', '') != '':
            filters.append(Q(pickup_person_id=int(request.GET['pickup_person_to_search'])))

        all_bills = Bill.objects.filter(*filters).order_by('-pickup_time', '-bill_number')
        all_pickup_persons = User.objects.filter(bill_pickup_person__isnull = False).distinct('id')

        if len(all_bills) > 0:
            # Calculate total number of packages and weight
            total_number_of_packages = 0
            total_weight = decimal.Decimal(0)
            for bill in all_bills:
                total_number_of_packages += 1
                if bill.weight_lb != None \
                        and bill.weight_lb != 0 \
                        and str(total_weight) != u'有些快递单没有重量':
                    total_weight += bill.weight_lb
                else:
                    total_weight = u'有些快递单没有重量'



            # Paginate all bills into different pages
            paged_bills = Paginator(all_bills, 300)  # Display 300 items every page
            if 'page_number_to_show' in request.GET:
                page_number_to_show = int(request.GET['page_number_to_show'])
            else:
                page_number_to_show = 1
            return render(request, 'gwstore/admincollectinfo.html',
                          {'bills_in_one_page': paged_bills.page(page_number_to_show),'all_pickup_persons':all_pickup_persons,
                           'total_number_of_packages': total_number_of_packages, 'total_weight': total_weight})
        else:
            return render(request, 'gwstore/admincollectinfo.html', {'bills_in_one_page': None, 'all_pickup_persons':all_pickup_persons})


@user_passes_test(is_admin)
def is_one_user_own_all_bills(request):
    bill_numbers = request.GET['bill_numbers_batch'].split(",")
    user_set = Bill.objects.filter(bill_number__in=bill_numbers).distinct('user')
    if len(user_set) == 1:
        return JsonResponse({'result': 'True', 'username': user_set[0].user.username})
    else:
        return JsonResponse({'result': 'False'})


@login_required()
def change_account(request):
    if request.method == 'GET':
        return render(request, 'gwstore/changeaccount.html')
    if request.method == 'POST':
        if 'password' in request.POST:
            user = User.objects.get(id=request.user.id)
            user.set_password(request.POST['password'])
            user.save()
            update_session_auth_hash(request, user)  # Update the session ID, because it is based on user's password.
            return HttpResponse('success')
        if 'email' in request.POST:
            user = User.objects.get(id=request.user.id)
            user.email = request.POST['email'].lower()
            user.save()
            return HttpResponse('success')


@user_passes_test(is_admin)
def summernote(request):
    if request.method == 'GET':
        htmls = HTMLCode.objects.filter(for_component=request.GET['for_component'])
        if len(htmls) == 0:
            html_code = HTMLCode()
        else:
            html_code = htmls[0]
        html_code.for_component = request.GET['for_component']

        return render(request, 'gwstore/summernote.html', {'html_code': html_code.html_code})
    else:
        try:
            htmls = HTMLCode.objects.filter(for_component=request.POST['for_component'])
            if len(htmls) == 0:
                html_code = HTMLCode()
            else:
                html_code = htmls[0]
            html_code.html_code = request.POST['html_code']
            html_code.for_component = request.POST['for_component']
            html_code.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'error': str(e)})


@user_passes_test(is_admin)
def update_weight(request):
    if request.method == 'POST':
        bill = Bill.objects.get(bill_number=int(request.POST['bill_number']))
        bill.weight_lb = float(request.POST['weight_lb'])
        bill.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'})


@user_passes_test(is_admin)
def admin_pickup_packages(request):
    if request.method == 'GET':
        filters = []
        if request.GET.get('bill_number_to_search', '') != '':
            filters.append(Q(bill_number__contains=int(request.GET['bill_number_to_search'])))
        if request.GET.get('user_name_to_search', '') != '':
            filters.append(Q(user__username=request.GET.get('user_name_to_search', '').lower()))
        if request.GET.get('status_code_to_search', '') != '':
            filters.append(Q(status_code=request.GET['status_code_to_search']))
        if request.GET.get('update_time_to_search', '') != '':
            filters.append(Q(update_time__gte=timezone.now() - datetime.timedelta(days=int(request.GET['update_time_to_search']))))

        all_bills = Bill.objects.filter(*filters).order_by('sender_district', 'user__username', '-bill_number')
        if len(all_bills) > 0:
            paged_bills = Paginator(all_bills, 30)  # Display 30 items every page
            if 'page_number_to_show' in request.GET:
                page_number_to_show = int(request.GET['page_number_to_show'])
            else:
                page_number_to_show = 1
            return render(request, 'gwstore/adminpickuppackages.html',
                          {'bills_in_one_page': paged_bills.page(page_number_to_show)})
        else:
            return render(request, 'gwstore/adminpickuppackages.html', {'bills_in_one_page': None})


def home(request):
    htmls = HTMLCode.objects.filter(for_component='Home Page')
    if len(htmls) > 0:
        html_code = htmls[0].html_code
    else:
        html_code = "此页面正在建设中。。。"
    return render(request, "gwstore/home.html", {'html_code': html_code})

def help_each_other(request):
    htmls = HTMLCode.objects.filter(for_component='Help Each Other')
    if len(htmls) > 0:
        html_code = htmls[0].html_code
    else:
        html_code = "暂无信息发布。。。"
    return render(request, "gwstore/helpeachother.html", {'html_code': html_code})

@login_required()
def bill_list(request):
    all_bills = Bill.objects.filter(user_id=request.user.id).order_by('-update_time', '-status_code', '-bill_number')
    return render(request, "gwstore/billlist.html", {'all_bills': all_bills})


@user_passes_test(is_admin)
def signature_pad(request):
    if request.method == 'GET':
        return render(request, "gwstore/signaturepad.html")


def batch_save_signature_and_send_email(pickup_person, bill_numbers, bill_status_code, signature_data_uri):
    all_bills = Bill.objects.filter(bill_number__in=bill_numbers)
    if bill_status_code == 'B':
        for bill in all_bills:
            # Change the status to Already Picked up
            bill.status_code = 'B'
            bill.status_description = '已经被联通Cote-Vertu收货点接收'
            # Save the signature
            bill.client_signature_data_uri = signature_data_uri
            bill.pickup_time = timezone.now()
            bill.pickup_person = pickup_person
            bill.email_sent_out_time = timezone.now()
            bill.save()
        # Save the bill in PDF and send it to user's email.
        save_batch_pdf_and_send_email(bill_numbers)
    if bill_status_code == 'B1':
        for bill in all_bills:
            # Change the status to Already Picked up, but the bill information is not complete.
            bill.status_code = 'B1'
            bill.status_description = '已经被联通Cote-Vertu收货点接收,但是快递单信息不完整'
            # Save the signature
            bill.client_signature_data_uri = signature_data_uri
            bill.pickup_time = timezone.now()
            bill.pickup_person = pickup_person
            bill.save()  # Will not generate the PDF and send the email until the bill is completed.


@user_passes_test(is_admin)
def batch_upload_signature_and_send_email(request):
    if request.method == 'POST':
        bill_numbers_batch = request.POST['bill_numbers_batch'].split(",")
        batch_save_signature_and_send_email(pickup_person=request.user, bill_numbers=bill_numbers_batch,
                                            bill_status_code=request.POST['status_code_to_be'],
                                            signature_data_uri=request.POST['client_signagure_data_uri'])
        return JsonResponse({'status': 'success'})


@login_required
def bill_input(request):
    if request.method == 'GET':
        if 'bill_number' in request.GET:
            # Modify existing bill
            if request.user.is_superuser:
                bill_form = BillForm(instance=Bill.objects.get(
                    # 'A' means the package is waiting for being picked up.
                    # 'B1' means the package has already been picked up but the bill information is not complete.
                    # 'B' means the package has already been picked up and the information is completed.
                    status_code__in=['A', 'B1', 'B'],
                    bill_number=int(request.GET['bill_number'])))
            else:
                # Normal user can only modify his own bill
                bill_form = BillForm(instance=Bill.objects.get(
                    user_id=request.user.id,
                    # 'A' means the package is waiting for being picked up.
                    # 'B1' means the package has already been picked up but the bill information is not complete.
                    status_code__in=['A', 'B1'],
                    bill_number=int(request.GET['bill_number'])))
        else:
            # Create a new bill
            bill_form = BillForm(initial={'item_1_quantity': '', 'uuid_for_avoiding_duplicate':str(uuid.uuid4())})

        all_history_sender_addresses = Bill.objects.filter(user_id=request.user.id).distinct('sender_name',
                                                                                             'sender_address',
                                                                                             'sender_phone',
                                                                                             'sender_post_code',
                                                                                             'sender_district')

        all_history_receiver_addresses = Bill.objects.filter(user_id=request.user.id).distinct('receiver_name',
                                                                                               'receiver_address',
                                                                                               'receiver_phone',
                                                                                               'receiver_post_code')
        return render(request, "gwstore/billinput.html",
                      {"bill_form": bill_form, "all_history_sender_addresses": all_history_sender_addresses,
                       "all_history_receiver_addresses": all_history_receiver_addresses})

    if request.method == 'POST':
        if (request.POST['bill_number'] != '0' ):
            # Modify existing bill
            if (request.user.is_superuser):
                bill = Bill.objects.get(bill_number=int(request.POST['bill_number']))
            else:
                # Normal user can only modify his own bill
                bill = Bill.objects.get(user_id=request.user.id, bill_number=int(request.POST['bill_number']))
            old_status_code = bill.status_code
            bill_form = BillForm(request.POST, instance=bill)
            if bill_form.is_valid():
                bill = bill_form.save(commit=False)
                if bill.status_code == 'B':  # The user may change the status code from 'B1' to 'B' by completing the missing information.
                    bill.status_description = u'已经被联通Cote-Vertu收货点接收'
                bill.save()
                # The status is changed from 'Picked up but incomplete information' to 'Picked up and complete information'
                if old_status_code == 'B1' and bill.status_code == 'B':
                    save_batch_pdf_and_send_email([bill.bill_number])  # Create the PDF and send the email.
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "failed", "error": bill_form.errors.as_ul()})
                # Modifying existing bill logic ends here

        else:  # Create a new bill
            bill_form = BillForm(request.POST)
            # Save the bill into database
            if bill_form.is_valid():
                bill = bill_form.save(commit=False)
                bill.bill_number = generate_bill_number()
                bill.user = request.user
                bill.status_code = 'A'
                bill.status_description = u'正在等待Cote-Vertu收货点收取包裹'
                bill.save()
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "failed", "error": bill_form.errors.as_ul()})
                # Creating a new bill logic ends here

# Log off the user
def logoff_user(request):
    logout(request)
    return HttpResponseRedirect("/")  # Return to the home page


# Login the user
def login_user(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'].lower(), password=request.POST['password'])
        if user != None:
            login(request, user)
            if request.POST['next'] != '':
                return JsonResponse({'status': 'success', 'next': request.POST['next']})
            else:
                return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'failed', 'error': "用户名或密码不正确。"})
    else:
        next_url = ''
        if 'next' in request.GET:
            next_url = request.GET['next']
        return render(request, "gwstore/login.html", {'next': next_url})


# Register a new user
def new_user(request):
    if request.method == 'GET':
        return render(request, "gwstore/newuser.html")
    else:
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            User.objects.create_user(username=user_form.cleaned_data['username'],
                                     email=user_form.cleaned_data['email'],
                                     password=user_form.cleaned_data['password'])
            user = authenticate(username=user_form.cleaned_data['username'],
                                password=user_form.cleaned_data['password'])
            user.username = user.username.lower()  # Convert all user names to lower case.
            user.email = user.email.lower() # Convert all users' emails to lower case.
            user.is_superuser = False
            user.save()
            login(request, user)
            return HttpResponse("success")
        else:
            return HttpResponse(str(user_form.errors.as_ul()))


# Check whether a user has already used the email address
def check_exist_email(request):
    if request.method == 'GET':
        users = User.objects.filter(email__iexact=request.GET['email'])
        if users.count() >= 1:
            return HttpResponse("false")  # Already used。
        else:
            return HttpResponse("true")  # Not used.


def check_exist_username(request):
    if request.method == 'GET':
        users = User.objects.filter(username__iexact=request.GET['username'])
        if users.count() >= 1:
            return HttpResponse("false")  # Already used
        else:
            return HttpResponse("true")  # Not used

def for_migration(request):
    all_bills = Bill.objects.all()
    for bill in all_bills:
        bill.uuid_for_avoiding_duplicate = str(uuid.uuid4())
        bill.save()
    return HttpResponse("Success!")
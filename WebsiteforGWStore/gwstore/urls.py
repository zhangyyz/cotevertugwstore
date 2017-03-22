from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    url(r'billinput/', views.bill_input, name="bill_input"),
    url(r'billlist/', views.bill_list, name="bill_list"),
    url(r'helpeachother/', views.help_each_other, name='help_each_other'),
    url(r'checkexistusername/', views.check_exist_username, name="check_exist_username"),
    url(r'checkexistemail/', views.check_exist_email, name="check_exist_email"),
    url(r'newuser/', views.new_user, name="new_user"),
    url(r'login/', views.login_user, name='login_user'),
    url(r'logoff/', views.logoff_user, name='logoff_user'),
    url(r'uploadsignature/', views.batch_upload_signature_and_send_email, name='upload_signature'),
    url(r'^$', views.home, name='home'),
    url(r'adminpickuppackages/', views.admin_pickup_packages, name='admin_pickup_packages'),
    url(r'signaturepad/', views.signature_pad, name='signature_pad'),
    url(r'htmleditor', views.summernote, name='summernote'),
    url(r'changeaccount', views.change_account, name='change_account'),
    url(r'updateweight/', views.update_weight, name='update_weight'),
    url(r'allbillssameuser/', views.is_one_user_own_all_bills, name='is_one_user_has_all_bills'),
    url(r'admincollectinfo/', views.admin_collect_info, name='admin_collect'),
    url(r'batchdownloadbillsexcel/', views.batch_download_bills_excel, name='batch_download_bills_excel'),
    url(r'batchdownloadbillspdf/', views.batch_download_bills_pdf, name='batch_download_bills_pdf'),
    url(r'batchdownloadbarcodes/', views.batch_download_barcodes, name='batch_download_barcodes'),
    url(r'resetpassword/', views.reset_password, name='reset_password'),
    url(r'nobillexportedbefore/', views.no_bill_exported_before, name='no_bill_exported_before'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
import os
import random
from threading import Lock
from django.db.models import Max
from .models import Bill
from PIL import Image
from django import template
import pdfkit
from django.core.mail import EmailMessage
from io import BytesIO
import datetime
from base64 import b64decode
from django.contrib.auth.models import User
import uuid
import re
from django.conf import settings

MY_BILLS_SAVING_PATH = settings.MY_BILLS_SAVING_PATH
MY_PATH_TO_WKHTMLTOPDF = settings.MY_PATH_TO_WKHTMLTOPDF
MY_BARCODE_SAVING_PATH = settings.MY_BARCODE_SAVING_PATH

lock = Lock()

def generate_bill_number():
    with lock:
        current_max_bill_number = Bill.objects.all().aggregate(current_max_bill_number=Max('bill_number'))[
            'current_max_bill_number']
        if (current_max_bill_number == None):
            return 9990000000
        return current_max_bill_number + 1


def save_barcodes_to_pdf(batch_bill_numbers):
    bill_template = template.loader.get_template("gwstore/barcodeprint.html")
    all_bills = Bill.objects.filter(bill_number__in=batch_bill_numbers).order_by('bill_number')
    bill_html = bill_template.render({'all_bills': all_bills})
    path_wkthmltopdf = MY_PATH_TO_WKHTMLTOPDF
    # Not in use>>>>>>>>>>
    """options = {
    'page-size': 'Letter',
    'margin-top': '0.05in',
    'margin-right': '1.5in',
    'margin-bottom': '0.05in',
    'margin-left': '0.05in',
    'encoding': "UTF-8",
    'no-outline': None
    }"""
    # <<<<<<<<<<<<<<<<<<<<<<

    options = {
        'page-size': 'Letter',
        'margin-top': '0.3in',
        'margin-right': '0.4in',
        'margin-bottom': '0.05in',
        'margin-left': '0.5in',
        'encoding': "UTF-8",
        'no-outline': None
    }

    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    # The file will be saved into folder
    now = datetime.datetime.now()
    save_to_directory = MY_BARCODE_SAVING_PATH.format(now.strftime('%Y%m%d'))
    if not os.path.exists(save_to_directory):
        os.makedirs(save_to_directory)
    output_pdf_path = os.path.join(save_to_directory, str(uuid.uuid4()) + ".pdf")
    pdfkit.from_string(input=bill_html, output_path=output_pdf_path, configuration=config, options=options)
    return output_pdf_path


def save_batch_bills_to_one_pdf(bill_numbers, save_to_directory, filename):
    all_bills = Bill.objects.filter(bill_number__in=bill_numbers).order_by('bill_number')
    for bill in all_bills:
        # Calculate the proportion between width and height, and set the proper value in the template.
        if bill.client_signature_data_uri is not None:
            im = Image.open(BytesIO(b64decode(bill.client_signature_data_uri.replace("data:image/png;base64,", ""))))
            width, height = im.size
        else:
            width = height = 1

        if width / height > 3:
            bill.client_signature_width = "90%"
            bill.client_signature_height = "auto"
        else:
            bill.client_signature_width = "auto"
            bill.client_signature_height = "100%"

    bill_template = template.loader.get_template("gwstore/batchbillprint.html")
    bill_html = bill_template.render({'all_bills': all_bills})
    path_wkthmltopdf = MY_PATH_TO_WKHTMLTOPDF
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    # The file will be saved into folder

    if not os.path.exists(save_to_directory):
        os.makedirs(save_to_directory)
    output_pdf_path = os.path.join(save_to_directory, filename)
    pdfkit.from_string(input=bill_html, output_path=output_pdf_path, configuration=config)
    return output_pdf_path


def save_batch_pdf_and_send_email(bill_numbers):
    bill_numbers.sort()
    now = datetime.datetime.now()
    if len(bill_numbers) > 1:
        filename = str(bill_numbers[0]) + "etc.pdf"
    else:
        filename = str(bill_numbers[0]) + ".pdf"
    output_pdf_path = save_batch_bills_to_one_pdf(bill_numbers,
                                                  save_to_directory=MY_BILLS_SAVING_PATH.format(now.strftime('%Y%m%d')),
                                                  filename=filename)

    # Send the email to user's emailbox
    all_bills = Bill.objects.filter(bill_number__in=bill_numbers)
    one_bill = all_bills[0]
    username = one_bill.user.username
    user = User.objects.get(username=username)

    email_163_pattern = re.compile(".*@126.com$|.*@163.com$")
    if email_163_pattern.match(user.email):
        message = EmailMessage(
        subject='您单号为{0}的包裹已被联通快递Cote-Vertu收货点收取。'.format( ",".join(map(str,bill_numbers))),
        body=u"""
您单号为{0}的包裹已经被联通快递Cote-Vertu收货点收取，快递单的详细信息请查询该Email的附件。

Cote-Vertu收货点的所有快递单信息会在每周一和周四统一上传到联通快递总部的网站　http://www.fastontime.com，所以请您耐心等待，在快递单信息被上传到总站以后您就可以在联通总部的网站上查询到您的包裹状态了。

打开附件的方法：因为您使用的是网易的邮箱，我们为了避免本Email被网易当成垃圾邮件，所以我们在附件的文件名里加入了空格。请您把附件下载后，删除文件名里的空格就可以正常打开了。给您造成不便，深表歉意！

谢谢您的支持！

""".format(",".join(map(str, bill_numbers))),
        to=[user.email])
        attachment = open(output_pdf_path, 'rb')
        message.attach("联通快递单.　　　pdf", attachment.read())
    else:
        message = EmailMessage(
        subject='您单号为{0}的包裹已被联通快递Cote-Vertu收货点收取。'.format( ",".join(map(str,bill_numbers))),
        body=u"""

您单号为{0}的包裹已经被联通快递Cote-Vertu收货点收取，快递单的详细信息请查询该Email的附件。

Cote-Vertu收货点的所有快递单信息会在每周一和周四统一上传到联通快递总部的网站 http://www.fastontime.com，所以请您耐心等待，在快递单信息被上传到总站以后您就可以在联通总部的网站上查询到您的包裹状态了。

谢谢您的支持！

""".format(",".join(map(str, bill_numbers))),
        to=[user.email])
        attachment = open(output_pdf_path, 'rb')
        message.attach(u'联通快递单.pdf', attachment.read())
    message.send()

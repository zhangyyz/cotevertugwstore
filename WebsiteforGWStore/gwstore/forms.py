from django import forms
from .models import Bill
from django.contrib.auth.models import User
from django.forms import ValidationError

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['bill_number', 'contain_dangerous_goods', 'sender_name', 'sender_address', 'sender_phone',
                  'sender_post_code', 'sender_district', 'receiver_name', 'receiver_address', 'receiver_phone',
                  'receiver_post_code', 'buy_package_lost_insurance', 'package_lost_insured_amount', 'package_lost_premium_amount',
                  'item_1_description', 'item_1_quantity', 'item_2_description', 'item_2_quantity',
                  'item_3_description', 'item_3_quantity', 'item_4_description', 'item_4_quantity',
                  'item_5_description', 'item_5_quantity', 'weight_lb', 'status_code', 'uuid_for_avoiding_duplicate']

    def clean(self):
        cleaned_data = self.cleaned_data
        contain_dangerous_goods = cleaned_data['contain_dangerous_goods']
        buy_package_lost_insurance = cleaned_data['buy_package_lost_insurance']
        package_lost_insured_amount = cleaned_data['package_lost_insured_amount']
        package_lost_premium_amount = cleaned_data['package_lost_premium_amount']

        #  Check whether it has dangerous goods
        if contain_dangerous_goods != 'No':
            raise ValidationError("包裹内包含危险物品，请联系我们的客服确认是否可以邮寄。")

        #  Check whether the user wants to buy insurance
        if buy_package_lost_insurance == 'Yes':
            if package_lost_insured_amount == None or package_lost_premium_amount == None:
                raise ValidationError("您选择了购买“包裹丢失”保险，所以需要输入要包裹内物品的总价值。")
            else:
                if abs(package_lost_premium_amount - package_lost_insured_amount * 0.05) >= 0.005:
                    raise ValidationError("保费应该是物品总价值的５％")
        else:
            cleaned_data['package_lost_insured_amount'] = 0
            cleaned_data['package_lost_premium_amount'] = 0



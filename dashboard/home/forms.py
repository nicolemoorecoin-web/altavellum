from dataclasses import fields
from django import forms 
#from .models import Cryptocurrency, Investment_Plan, Investment
from .models import Investment, Withdraw, Crypto_Withdraw, ScreenshotOFPayment, UserAddress, PaymentScreenshot, User_Withdrawal #, AccountVerification
#from usersbank.models import UserTradingAccount
from cloudinary.models import CloudinaryField

class DocumentForm(forms.ModelForm):
    file = CloudinaryField()

    class Meta:
        model = PaymentScreenshot
        fields = ['file', 'name']

        widgets = {
			#'image': forms.(attrs={'class': 'form-control'}),
			'name': forms.TextInput(attrs={'class': 'form-control', 'value': '', 'id': 'elder', 'type': 'hidden'}),
			#'investment_connected': forms.TextInput(attrs={'class': 'form-control', 'value': '', 'id': 'second', 'type': 'hidden'}),

		}

choice_list = ['basic', 'advanced']

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = ('investor', 'investment_plan', 'amount_in_USD', 'cryptocurrency')

        widgets = {
            'investor': forms.TextInput(attrs={'class': 'form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent', 'value': '', 'id': 'elder', 'type': 'hidden'}),
            'investment_plan': forms.Select(attrs={'class': 'form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent'}),
            'cryptocurrency': forms.Select(attrs={'class': 'form-select mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:bg-navy-700 dark:hover:border-navy-400 dark:focus:border-accent'}),
            'amount_in_USD': forms.TextInput(attrs={'class': 'form-input mt-1.5 h-12 w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent'}),
        }



class WithdrawForm(forms.ModelForm):
	#id_front = CloudinaryField()
	#id_back = CloudinaryField()
	class Meta:
		model = Withdraw
		fields = ('investor',  'id_front', 'id_back', 'bank_name', 'account_number', 'amount_in_USD', 'routine_number', 'ssn')

		widgets = {
			'investor': forms.TextInput(attrs={'class': 'form-control', 'value': '', 'id': 'elder', 'type': 'hidden'}),
			'amount_in_USD': forms.TextInput({'class': 'form-control'}),
		}

class ScreenShotForm(forms.ModelForm):
    file = CloudinaryField()

    class Meta:
        model = ScreenshotOFPayment
        fields = ['file']


	#	widgets = {
	#		'street_address': forms.TextInput({'class': 'form-control'}),
	#		'city': forms.TextInput({'class': 'form-control'}),
	#		'postal_code': forms.TextInput({'class': 'form-control'}),
	#		'country': forms.TextInput({'class': 'form-control'}),
	#	}

class AddressForm(forms.ModelForm):
	class Meta:
		model = UserAddress
		fields = ('user', 'street_address', 'city',  'postal_code', 'country', 'phone_number')

		widgets = {
			'user': forms.TextInput(attrs={'class': 'form-input peer w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:z-10 hover:border-slate-400 focus:z-10 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent', 'value': '', 'id': 'elder', 'type': 'hidden', 'placeholder': ''}),
			'street_address': forms.TextInput({'class': 'form-input peer w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:z-10 hover:border-slate-400 focus:z-10 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent', 'placeholder': 'Street Address'}),
			'city': forms.TextInput({'class': 'form-input peer w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:z-10 hover:border-slate-400 focus:z-10 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent', 'placeholder': 'City'}),
			'postal_code': forms.TextInput({'class': 'form-input peer w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:z-10 hover:border-slate-400 focus:z-10 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent', 'placeholder': 'Postal Code'}),
			'country': forms.TextInput({'class': 'form-input peer w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:z-10 hover:border-slate-400 focus:z-10 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent', 'placeholder': 'Country'}),
			'phone_number': forms.TextInput({'class': 'form-input peer w-full rounded-lg border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:z-10 hover:border-slate-400 focus:z-10 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent', 'placeholder': 'Phone Number'}),
			#'payment_gateway': forms.Select(attrs={'class': 'form-control'}),
			#'wallet_address': forms.TextInput(attrs={'class': 'form-control'}),
			
		}


class WithdrawalForm(forms.ModelForm):
    file = CloudinaryField()

    class Meta:
        model = User_Withdrawal
        fields = ['name', 'bank_name', 'account_number', 'amount_in_USD', 'routine_number', 'ssn', 'id_front', 'id_back',]

        widgets = {
			#'image': forms.(attrs={'class': 'form-control'}),
			'name': forms.TextInput(attrs={'class': 'form-control', 'value': '', 'id': 'elder', 'type': 'hidden'}),
		#	'withdraw_option': forms.Select(attrs={'class': 'form-control'}),
			#'investment_connected': forms.TextInput(attrs={'class': 'form-control', 'value': '', 'id': 'second', 'type': 'hidden'}),
			'bank_name': forms.TextInput({'class': 'form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent'}),
			#'wallet_address': forms.TextInput({'class': 'form-control'}),
			'account_number': forms.TextInput({'class': 'form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent'}),
			'amount_in_USD': forms.TextInput({'class': 'form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent'}),
			'routine_number': forms.TextInput({'class': 'form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent'}),
			'ssn': forms.TextInput({'class': 'form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent'}),


		}



class CryptoWithdrawalForm(forms.ModelForm):
	#id_front = CloudinaryField()
	#id_back = CloudinaryField()
	class Meta:
		model = Crypto_Withdraw
		fields = ('investor', 'payment_gateway', 'amount_in_USD', 'wallet_address', 'tan_code',)

		widgets = {
			'investor': forms.TextInput(attrs={'class': 'form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent', 'value': '', 'id': 'elder', 'type': 'hidden'}),
			'amount_in_USD': forms.TextInput({'class': 'form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent'}),
			'payment_gateway': forms.Select(attrs={'class': 'form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent'}),
			'wallet_address': forms.TextInput(attrs={'class': 'form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent'}),
			'tan_code' : forms.TextInput(attrs={'class': 'form-input peer w-full rounded-full border border-slate-300 bg-transparent px-3 py-2 pl-9 placeholder:text-slate-400/70 hover:border-slate-400 focus:border-primary dark:border-navy-450 dark:hover:border-navy-400 dark:focus:border-accent'}),
		}

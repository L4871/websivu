from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
# Modify the userCreationForm

class SignUpForm(UserCreationForm):
	GENDRES =(
				('m', 'Male'),
				('f', 'Female'),

		)
	gender = forms.ChoiceField(choices=GENDRES)
	weight = forms.DecimalField(min_value=0)



	class Meta:
		model = User
		fields = ['username',
				'password1',
				'password2',
				'weight',
				'gender',
			]
		help_texts ={
		'username' : None,
		}

class EditProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['weight',]

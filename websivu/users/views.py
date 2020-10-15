from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, EditProfileForm
from .models import Profile, FavoriteRecipes
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth import authenticate, login
from django.contrib import messages 
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect



def register(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			user.refresh_from_db()  # load the profile instance created by the signal
			user.profile.gender = form.cleaned_data.get('gender')
			user.profile.weight = form.cleaned_data.get('weight')
			user.profile.age = form.cleaned_data.get('age')
			user.profile.save()
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=user.username, password=raw_password)
			login(request, user)
			return HttpResponseRedirect('/recipe/')
		else:
			messages.error(request, "Error")
	else:
		form = SignUpForm()
		return render(request, 'users/register.html', {'form': form})



@login_required
def profile(request):
	user = User.objects.get(pk=request.user.id)
	profileObj = Profile.objects.get(user_id=user.id)
	args = {'user' : request,
			'profile' : profileObj,}
	return render (request, 'users/profile.html', args)




def favoriteRecipe(request, id):
	recipe = get_object_or_404(Profile, id=id)
	if recipe.favorites.filter(id=request.user.id).exists():
		recipe.favorites.remove(request.user)
	else:
		recipe.favorites.add(request.user)
	return HttpResponseRedirect()

@login_required
def editProfile(request):
	profile = get_object_or_404(Profile, user_id=request.user.id)
	template_name = 'users/profile_edit_form.html'
	if request.method == 'GET':
		profile_form = EditProfileForm(request.GET, instance=profile)
	
	if request.method == 'POST':
		profile_form = EditProfileForm(request.POST)
		if profile_form.is_valid():
			profileInstance = profile_form.save(commit=False)
			profileInstance.id = profile.id
			profileInstance.user_id = request.user.id
			profileInstance.save()

		return HttpResponseRedirect('/profile/')


	return render(request, template_name, {
			'profile_form':profile_form,
			})
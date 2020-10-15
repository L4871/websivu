from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views.generic import (ListView 
									,DetailView
									,CreateView
									,UpdateView
									,DeleteView
									,View)
from .models import Ingredient, Recipe, RecipeIngredients, RecipeMealplan, Mealplan
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import CreateRecipe, AddIngredient, IngredientFormset, CreateMealplan,RecipesFormset, generateRecipesFormset
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from .filters import RecipeFilter
from users.models import FavoriteRecipes, Profile

def newIngredient(request):
	if request.method == 'POST':
		form = AddIngredient(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect("")

	else:
		form = AddIngredient()
		return render(request, 'recipe/add_ingredient.html', {'form' : form})



def newRecipe(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/login/')
	elif request.user.is_authenticated:
		template_name = 'recipe/recipe_form.html'

		if request.method == 'GET':
			recipe_form = CreateRecipe(request.GET or None)
			formset = IngredientFormset(queryset=Ingredient.objects.filter(id=RecipeIngredients.objects.first().id))

		elif request.method == 'POST':
			recipe_form = CreateRecipe(request.POST)
			formset = IngredientFormset(request.POST)
			if recipe_form.is_valid() and formset.is_valid():
				savedRecipe = recipe_form.save(commit=False)
				savedRecipe.author = request.user
				savedRecipe.save()
				for form in formset:
					ingredientEntry = form.save(commit=False)
					ingredientEntry.recipe_id = savedRecipe.id
					ingredientEntry.save()

				return HttpResponseRedirect('/recipe/view/' + savedRecipe.slug)
		return render(request, template_name, {
			'recipe_form' : recipe_form,
			'formset' : formset
			})

def newMealplan(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/login/')
	elif request.user.is_authenticated:
		template_name = 'recipe/mealplan_form.html'

		if request.method == 'GET':
			mealplan_form = CreateMealplan(request.GET or None)
			formset = RecipesFormset(queryset=Recipe.objects.filter(id=RecipeIngredients.objects.first().id))

		elif request.method == 'POST':
			mealplan_form = CreateMealplan(request.POST)
			formset = RecipesFormset(request.POST)
			if mealplan_form.is_valid() and formset.is_valid():
				savedMealplan = mealplan_form.save(commit=False)
				savedMealplan.createdBy = request.user
				savedMealplan.save()
				for form in formset:
					recipeEntry = form.save(commit=False)
					recipeEntry.mealplan_id = savedMealplan.id
					recipeEntry.save()
				return HttpResponseRedirect('/mealplans/' + str(savedMealplan.id))

		return render(request, template_name, {
			'mealplan_form':mealplan_form,
			'formset':formset
			})



class RecipeListView(ListView):

	model = Recipe
	template_name = 'recipe/recipe.html'
	context_object_name = "recipes"



	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['breakfasts'] = RecipeFilter(self.request.GET, queryset=Recipe.objects.filter(meal="Breakfast"))
		context['snacks'] = RecipeFilter(self.request.GET, queryset=Recipe.objects.filter(meal="Snack"))
		context['lunches'] = RecipeFilter(self.request.GET, queryset=Recipe.objects.filter(meal="Lunch"))
		context['dinners'] = RecipeFilter(self.request.GET, queryset=Recipe.objects.filter(meal="Dinner"))

		return context

class MealplanListView(ListView):
	model = Mealplan
	template_name = 'recipe/mealplans.html'
	context_object_name = "mealplans"

def mealplanDetailView(request,pk):
	mealplanInstance = Mealplan.objects.get(pk=pk)
	recipeMealplanInstance = RecipeMealplan.objects.filter(mealplan_id=mealplanInstance.id).all()
	recipeInstances = Recipe.objects.filter(id=recipeMealplanInstance[0].recipe_id).first()
	args = {'mealplan' : mealplanInstance,
			}

	return render(request,'recipe/mealplan_detail.html',args)

def recipeDetailView(request,slug):
	isFavorite = False
	recipeInstance = get_object_or_404(Recipe, slug=slug)
	favorite = FavoriteRecipes.objects.filter(favoriteRecipe_id=recipeInstance.id).first()
	if favorite != None:
		isFavorite = True
	recipeIngredientsInstance = RecipeIngredients.objects.filter(recipe_id=recipeInstance.id).first()
	args = {'recipe' : recipeInstance,
			'recipeIngredient' : recipeIngredientsInstance,
			'liked':isFavorite}
	return render(request,'recipe/recipe_detail.html', args)


def recipeFavorite(request,slug):
	recipe = get_object_or_404(Recipe,slug=slug)
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/login/')
	else:
		#if this recipe is in this users favorite recipes
		
		if FavoriteRecipes.objects.filter(user_id=request.user.id,favoriteRecipe_id=recipe.id):
			FavoriteRecipes.objects.filter(user_id=request.user.id,favoriteRecipe_id=recipe.id).first().delete()
		else:
			FavoriteRecipes.objects.create(user_id=request.user.id,favoriteRecipe_id=recipe.id)
	return HttpResponseRedirect(recipe.get_absolute_url())



def editMealplan(request,pk):
	mealplan = get_object_or_404(Mealplan,pk=pk)
	recipes = RecipeMealplan.objects.filter(mealplan_id=pk)
	if mealplan.createdBy != request.user:
		return HttpResponseRedirect('/login/')
	else:
		template_name = 'recipe/edit_mealplan_form.html'
		if request.method == "POST":
			mealplan_form = CreateMealplan(request.POST)
			formset = RecipesFormset(request.POST,queryset=recipes)

			if mealplan_form.is_valid() and formset.is_valid():
				editMealplan = mealplan_form.save(commit=False)
				mealplan.mealplan_name = editMealplan.mealplan_name
				mealplan.save()
				# delete old recipes from mealplan
				for olds in recipes:
					olds.delete()
				# add recipes from new form
				for form in formset:
					recipeEntry = form.save(commit=False)
					recipeEntry.mealplan_id = mealplan.id
					recipeEntry.save()

				return HttpResponseRedirect('/mealplans/' + str(mealplan.id))
			else:
				print(formset.errors)

		elif request.method == "GET":
			mealplan_form = CreateMealplan(instance=mealplan)
			formset = RecipesFormset(queryset=recipes)

		return render(request, template_name, {
			'mealplan_form':mealplan_form,
			'formset':formset
			})


def editRecipe(request,slug):
	recipe = get_object_or_404(Recipe,slug=slug)
	recipesIngredients = RecipeIngredients.objects.filter(recipe_id=recipe.id)
	if recipe.author != request.user:
		return HttpResponseRedirect('/login/')
	else:
		template_name = 'recipe/recipe_edit_form.html'
		if request.method =="POST":
			recipe_form = CreateRecipe(request.POST)
			formset = IngredientFormset(request.POST)


			if recipe_form.is_valid() and formset.is_valid():
				recipeEntry = recipe_form.save(commit=False)
				recipe.recipe = recipeEntry.recipe
				recipe.description = recipeEntry.description
				recipe.diet = recipeEntry.diet
				recipe.save()
				
				for olds in recipesIngredients:
					olds.delete()				

				for form in formset:
					ingredient = form.save(commit=False)
					ingredient.recipe_id = recipe.id
					ingredient.save()

				return HttpResponseRedirect('/recipe/view/' + slug)
				

		elif request.method == "GET":
			recipe_form = CreateRecipe(instance = recipe)
			formset = IngredientFormset(queryset=recipesIngredients)

		return render(request, template_name, {
			'recipe_form':recipe_form,
			'formset':formset
			})

class RecipeDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
	model = Recipe
	success_url = '/'

	def test_func(self):
		recipe = self.get_object()
		if self.request.user == recipe.author:
			return True
		return False



def deleteMealplan(request,pk):
	mealplan = get_object_or_404(Mealplan,pk=pk)
	if mealplan.createdBy != request.user:
		return HttpResponseRedirect('/login/')
	else:
		if request.POST:
			mealplan.delete()

	return HttpResponseRedirect('/mealplans')

def generateMealplan(request):
	template_name = 'recipe/mealplan_generator.html'
	meal_amount = 4
	mealplanInstance = Mealplan.objects.first()
	if not request.user.is_anonymous:
		profileObject = Profile.objects.filter(user_id=request.user.id).first()
		recipes = mealplanInstance.generateMealplan(profileObject.getCalories())
	else:
		recipes = mealplanInstance.generateMealplan(2600)
	if request.method == 'GET':
		formset = RecipesFormset(queryset=recipes)

	args = {
			'recipes' : recipes
			}
	#get_mealplans
	return render(request,'recipe/mealplan_generate.html',args)
# https://www.youtube.com/watch?v=QDdLvImfq_g
class AjaxHandlerView(View):
	def get(self, request):
		text = request.GET.get('button_text')
		return render(request,'recipe/mealplan_generate.html')
	def post(self,request):
		text = request.POST.get('button_text')
		return render(request,'recipe/mealplan_generate.html')



from django import forms
from django.contrib.auth.models import User
from .models import Recipe, RecipeIngredients, Ingredient, RecipeMealplan, Mealplan
from django.forms import modelformset_factory
class CreateRecipe(forms.ModelForm):
	recipe = forms.CharField(label='',
								widget=forms.TextInput(attrs={"placeholder": "Your Title"}))
	description = forms.CharField(label='',widget=forms.Textarea(attrs={"placeholder":"Instructions"}),required=False)
	
	class Meta:
		model = Recipe

		fields = ['recipe',
				'description',
				'meal',
				'diet'
				]







IngredientFormset = modelformset_factory(
	RecipeIngredients,
	fields=('ingredient', 'amount'),
	extra=1,
	
)


class AddIngredient(forms.ModelForm):
	class Meta:
		model = Ingredient
		fields = ['ingredient',
				'price',
				'fats',
				'carbs',
				'protein'
		]

class CreateMealplan(forms.ModelForm):
	mealplan_name = forms.CharField(label='', widget=forms.TextInput(attrs={"placeholder":"Mealplan name"}))
	class Meta:
		model = Mealplan
		fields = ['mealplan_name']

RecipesFormset = modelformset_factory(
	RecipeMealplan,
	fields=('recipe',),
	extra=1,

)

generateRecipesFormset = modelformset_factory(
	Recipe,
	fields=('recipe','recipeKcal'),
	extra=0,

)
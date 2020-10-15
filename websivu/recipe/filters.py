import django_filters
from .models import Recipe
from django import forms


class RecipeFilter(django_filters.FilterSet):

	meal = django_filters.ChoiceFilter(choices=Recipe.MEAL_CHOICES, widget=forms.RadioSelect,required=False)
	diet = django_filters.ChoiceFilter(choices=Recipe.DIET_CHOICES, widget=forms.RadioSelect,required=False)
	class Meta:
		model = Recipe
		fields = {
			'recipe' : ['icontains'],
		}

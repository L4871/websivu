from django.urls import path, include
from .views import RecipeListView, RecipeDeleteView, newRecipe, recipeDetailView, MealplanListView, mealplanDetailView, newMealplan, deleteMealplan, editMealplan, editRecipe, generateMealplan, AjaxHandlerView,testCards
from recipe import views



urlpatterns = [
    path('add/', views.newIngredient, name='add_ingredient.html'),


    path('mealplans/', include([
        path('new', views.newMealplan, name='mealplan-create'),
        path('<int:pk>', mealplanDetailView, name='recipe-mealplan-detail'),
        path('<int:pk>/delete/', views.deleteMealplan, name='deleteMealplan'),
        path('<int:pk>/edit/', views.editMealplan, name='edit-mealplan'),
        path('', views.generateMealplan, name='generate-mealplan'),
        path('refresh', AjaxHandlerView.as_view(), name='refresh-mealplan'),
        ])),


    path('recipe/',include([
        path('', RecipeListView.as_view() ,name="recipe-recipe"),
        path('view/<slug:slug>/', views.recipeDetailView ,name="recipe-detail"),
        path('new/', views.newRecipe, name="recipe-create"),
        path('edit/<slug:slug>/', views.editRecipe ,name="recipe-update"),
        path('delete/<slug:slug>/', RecipeDeleteView.as_view() ,name="recipe-delete"),
        path('favorite/<slug:slug>', views.recipeFavorite ,name="recipeFavorite"),
        ]))

]


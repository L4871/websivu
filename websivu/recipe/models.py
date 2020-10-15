from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify
import random
class MacroCatagories(models.Model):
	CATEGORIES =(
				('n', 'Neutral'),
				('hop', 'High on protein'),
				('hof', 'High on fat'),
				('hoc', 'High on carbs')
		)
	macro_category = models.CharField(max_length=3, choices=CATEGORIES,default='n',blank=True)
	sec_macro_category= models.CharField(max_length=3, choices=CATEGORIES,blank=True,null=True)


class Mealplan(models.Model):
	mealplan_name = models.CharField(max_length=50)
	recipes = models.ManyToManyField('Recipe',through="RecipeMealplan")
	createdBy = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

	def getMealplanRecipes(self):
		recipes= []
		for recipe in self.recipes.all():
			recipes.append(recipe)
		return recipes


	def calculateMealplanTotalKcal(self):
		meals = self.getMealplanRecipes()
		total = 0
		for meal in meals:
			total = total + meal.getRecipeKcal()

		return total

	def calculateMealplanTotalMacros(self):
		meals = self.getMealplanRecipes()
		total = [0,0,0]
		for meal in meals:
			total[0] = total[0] + meal.getRecipeMacros()[0]
			total[1] = total[1] + meal.getRecipeMacros()[1]
			total[2] = total[2] + meal.getRecipeMacros()[2]
		return total

	def calculateMealplanPrice(self):
		meals = self.getMealplanRecipes()
		price = 0
		for meal in meals:
			price = price + meal.getRecipePrice()
		return price

		#VIP
	def checkDuplicates(self, elements):

		return 0

	def getMealplanShoppinglist(self):
		recipes = self.getMealplanRecipes()
		mealPlanShoppinglist = []
		recipeInstances = []
		for meal in recipes:
			recipeIngredientObjects = RecipeIngredients.objects.filter(recipe=meal).all()
			for recipe in recipeIngredientObjects:
				item = str(recipe.amount) + "g " + str(recipe.ingredient)
				mealPlanShoppinglist.append(item)
				recipeInstances.append(recipe)
				

		for meal in recipes:
			recipeIngredientObjects = RecipeIngredients.objects.filter(recipe=meal).all()
			for recipe in recipeIngredientObjects:
				if recipe in duplicates:
					pass


		return mealPlanShoppinglist

	def selectNewFood(self, meal):
		recipes = Recipe.objects.filter(meal=meal)
		recipe = random.choice(recipes)
		return recipe

	def generateMealplan(self, userKcal):
		#Get different Recipe objects based on meals
		breakfasts = Recipe.objects.filter(meal='Breakfast').values_list('recipeKcal','recipe')
		dinners = Recipe.objects.filter(meal='Dinner').values_list('recipeKcal','recipe')
		orederedBreakfasts = breakfasts.order_by('recipeKcal')
		orderedDinners = dinners.order_by('recipeKcal')

		#calories from foods with least calories
		minKcals = orederedBreakfasts[0][0] + orderedDinners[0][0]
		#calories from foods with highest calories
		maxKcals = orederedBreakfasts[len(orederedBreakfasts)-1][0] + orderedDinners[len(orderedDinners)-1][0]
		maxKcalsDinner = orderedDinners[len(orderedDinners)-1][0]
		minKcalsDinner = orderedDinners[0][0]

		breakfast = self.selectNewFood('Breakfast')
		lunch = self.selectNewFood('Lunch')
		while(True):
			remainingKcal = userKcal - breakfast.recipeKcal - lunch.recipeKcal
			#tarkista onko olemassa kahta ateriaa josta saa liian vähän kaloreita että kalori tavoite ei täyty
			if remainingKcal < minKcals or remainingKcal > maxKcals:
				lunch = self.selectNewFood('Lunch')
			else:
				break;

		nightSnack = self.selectNewFood('Breakfast')
		while(True):
			if nightSnack == breakfast:
				nightSnack = self.selectNewFood('Breakfast')
			elif maxKcalsDinner + nightSnack.recipeKcal < remainingKcal or minKcalsDinner + nightSnack.recipeKcal > remainingKcal:
				nightSnack = self.selectNewFood('Breakfast')
			else:
				remainingKcal = remainingKcal - nightSnack.recipeKcal
				break;

		dinner = self.selectNewFood('Dinner')
		while(True):
			#mealplan total kcal = userKcal +- 100
			if remainingKcal + 100 >  dinner.recipeKcal and remainingKcal - 100 < dinner.recipeKcal:
				remainingKcal = remainingKcal - dinner.recipeKcal
				break;
			else:
				dinner = self.selectNewFood('Dinner')
		calories = breakfast.recipeKcal + lunch.recipeKcal + dinner.recipeKcal + nightSnack.recipeKcal
		mealList = [breakfast, lunch, dinner, nightSnack]
		return mealList



# Create your models here.
class Ingredient(models.Model):
	ingredient = models.CharField(max_length=50, unique = True)
	price = models.DecimalField(max_digits=7, decimal_places=6, blank=True, null=True)
	fats = models.DecimalField(max_digits=5, decimal_places=4)
	carbs = models.DecimalField(max_digits=5, decimal_places=4)
	protein = models.DecimalField(max_digits=5, decimal_places=4)

	def __str__(self):
		return self.ingredient
	#returns Ingredient objects macros
	def getIngredientMacros(self):
		macros = []
		macros.append(self.fats)
		macros.append(self.carbs)
		macros.append(self.protein)
		return macros

class Recipe(models.Model):
	keto ="Keto"
	veg = "Veg"
	pesc = "Pesce" #seafood
	paleo = "Paleo"
	dairy = "Dairy free"
	DIET_CHOICES= [
		(keto, 'Ketogenic'),
		(veg, 'Vegetarian'),
		(pesc, 'Pescetarian'),
		(paleo,'Paleo'),
		(dairy, 'Dairy free')
	]

	american = "amr"
	italian = "itl"
	asian = "asi"
	mexican = "mex"
	french = "fr"
	bbq = "bbq"
	easy = "ez"
	cheap = "cheap"


	TYPE_CHOICES=[
		(american,'American'),
		(italian,'Italian'),
		(asian,'Asian'),
		(mexican,'Mexican'),
		(french,'French'),
		(bbq,'BBQ'),
		(easy,'Easy'),
		(cheap,'Cheap'),
	]
	breakfast = 'Breakfast'
	snack = 'Snack'
	lunch = 'Lunch'
	dinner = 'Dinner'
	MEAL_CHOICES=[
		(breakfast, 'Breakfast'),
		(snack, 'Snack'),
		(lunch, 'Lunch'),
		(dinner, 'Dinner'),

	]

	recipe = models.CharField(max_length=50)
	slug = models.SlugField(unique=True)
	ingredients = models.ManyToManyField('Ingredient',through="RecipeIngredients")
	attribute = models.CharField(max_length=20, blank=True, null=True) # vegan etc
	description = models.TextField()
	author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	meal = models.CharField(max_length=20,choices=MEAL_CHOICES, blank=True, null=True) # breakfast etc..
	image = models.ImageField(upload_to='meal_image', blank=True)
	category = models.ForeignKey(MacroCatagories, on_delete=models.CASCADE,blank=True, null=True) # 'high on protein etc' this should come be set based on macros muuta nimi?
	recipeKcal = models.IntegerField(blank=True, null=True)
	allergies = models.CharField(max_length=15, blank=True, null=True)
	diet = models.CharField(max_length=15, choices=DIET_CHOICES, blank=True)
	country = models.CharField(max_length=10, choices=TYPE_CHOICES, blank=True) #mistä maasta
	#kuva, type(high on protein..)
	def __str__(self):
		return self.recipe

	def get_absolute_url(self):
		return reverse('recipe-detail', kwargs={'slug': self.slug})
# returns all ingredient objects for recipe in dict 
	def getRecipeIngredients(self):
		ingredientList = []
		for ingredient in self.ingredients.all():

			ingredientList.append(ingredient)

		recipeIngredientList = {'name' : self.recipe,
								'ingredients' : ingredientList}

		return recipeIngredientList



	def getRecipeObjects(self):
		return self.recipe

	def getRecipeKcal(self):
		return self.recipeKcal

#returns recipes macros as fats/carbs/protein
	def getRecipeMacros(self):
		counter = 0
		recipeIngredientObjects = RecipeIngredients.objects.filter(recipe_id=self)
		macros = recipeIngredientObjects[0].countRecipeMacros()
		for i in macros:
			macros[counter] = round(i)
			counter = counter +1
		return macros

	def getRecipePrice(self):
		recipeIngredientObjects = RecipeIngredients.objects.filter(recipe_id=self)
		return recipeIngredientObjects[0].calculateRecipePrice()







class RecipeMealplan(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	mealplan = models.ForeignKey(Mealplan, on_delete=models.CASCADE, null = False)


	def getRecipeIngredientObject(self):
		recipeIngredientObjects = RecipeIngredients.objects.filter(recipe=self.recipe).all()




class RecipeIngredients(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
	amount = models.IntegerField()
	kcal = models.IntegerField(blank=True, null = True) # how many calories this meal has based on users ingredient amount




	def getRecipeIngredientObjects(self):
		riObjects = RecipeIngredients.objects.filter(recipe=self.recipe).all()
		return riObjects
	#returns list of ingredients
	def getIngredientList(self):
		ingredientObjects = self.recipe.getRecipeIngredients()
		objects = RecipeIngredients.objects.filter(recipe=self.recipe).all()
		amountOfIngredient = []
		for o in objects:
			amountOfIngredient.append(o.amount)
		ingredients = []
		for i in ingredientObjects['ingredients']:
			ingredients.append(i.ingredient)

		ingredientList = zip(ingredients ,amountOfIngredient)
		return ingredientList

	#returns recipes macros as fats/carbs/protein
	def countRecipeMacros(self):
		recipeIngredients = self.recipe.getRecipeIngredients()
		ingredientObjects = recipeIngredients['ingredients']
		recipeObject = Recipe.getRecipeObjects(self)
		recipeIngredientObjects = RecipeIngredients.objects.filter(recipe=recipeObject).all()
		macroList = [0,0,0]
		counter = 0
		#looppaa recipe ingredient objectit saat ainesosan määrän
		for i in ingredientObjects:
			macroList[0] = macroList[0] + i.fats * recipeIngredientObjects[counter].amount
			macroList[1] = macroList[1] + i.carbs * recipeIngredientObjects[counter].amount 
			macroList[2] = macroList[2] + i.protein * recipeIngredientObjects[counter].amount 
			counter = counter + 1
		macroList[0] = round(macroList[0],0)
		macroList[1] = round(macroList[1],0)
		macroList[2] = round(macroList[2],0)
		return macroList

	def calculateIngeredientKcal(self):
		kcal = self.ingredient.fats * self.amount * 9
		kcal = kcal + self.ingredient.carbs * self.amount * 4
		kcal = kcal + self.ingredient.protein * self.amount * 4
		kcal = round(kcal,0)
		return kcal

	def calculateRecipeCalories(self):
		ingredients = RecipeIngredients.objects.filter(recipe_id=self.recipe_id).all()
		kcal = 0
		for i in ingredients:
			kcal = kcal + i.kcal
		return kcal



	def calculateRecipePrice(self):
		price = 0
		ingredientObjects = self.recipe.getRecipeIngredients()
		objects = RecipeIngredients.objects.filter(recipe=self.recipe).all()
		for i in objects:
			price = price + i.amount * i.ingredient.price
		return round(price,2)




	#updates kcal field when RecipeIgnredient object is saved
	def save(self, *args, **kwargs):
		self.kcal = self.calculateIngeredientKcal() # adds ingredient calories to database
		# add category to Recipe high on protein etc
		obj = super(RecipeIngredients, self).save()
		# save recipes calories
		recipe = Recipe.objects.filter(recipe=self.recipe_id).first()
		self.recipe.recipeKcal = self.calculateRecipeCalories()
		super(Recipe,self.recipe).save()


	def delete(self, *args, **kwargs):
		#if Ingredient is deleted from Recipe update Recipe calories
		recipe = Recipe.objects.filter(recipe=self.recipe_id).first()
		super(RecipeIngredients,self).delete()
		self.recipe.recipeKcal = self.calculateRecipeCalories()
		super(Recipe,self.recipe).save()


def create_slug(instance, new_slug=None):
	slug = slugify(instance.recipe)
	if new_slug is not None:
		slug = new_slug
	qs = Recipe.objects.filter(slug=slug).order_by("-id")
	exists = qs.exists()
	if exists:
		new_slug = "%s-%s" %(slug, qs.first().id)
		return create_slug(instance, new_slug=new_slug)
	return slug

def pre_save_recipe_reciver(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_slug(instance)


pre_save.connect(pre_save_recipe_reciver,sender=Recipe)
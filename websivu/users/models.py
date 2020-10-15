import sys
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from recipe.models import Recipe, Mealplan



class Profile(models.Model):
	GENDERS = (
			('m', 'male'),
			('f', 'female')
		)

	user = models.OneToOneField(User, on_delete = models.CASCADE)
	gender = models.CharField(max_length=1, choices=GENDERS,default='m',blank=True,)
	weight = models.DecimalField(max_digits=6, decimal_places=2,blank=True, null=True)
	favorites = models.ManyToManyField(Recipe,through="FavoriteRecipes", blank=True)
	fats = models.IntegerField(blank=True, null=True)
	carbs = models.IntegerField(blank=True, null=True)
	protein = models.IntegerField(blank=True, null=True)
	#age, yhteys resepti taulukkoon (omat reseptit), suosikit


	@receiver(post_save, sender=User)
	def create_user_profile(sender, instance, created, **kwargs):
		if created:
			Profile.objects.create(user=instance)
			instance.profile.save()



	@receiver(post_save, sender=User)
	def save_user_profile(sender, instance, **kwargs):
		instance.profile.save()



	def getCalories(self):
		inTakeCalories = self.weight * Decimal(2.2) * 17 + 100
		inTakeCalories = round(inTakeCalories,0)
		return inTakeCalories

	#returns as protein fats carbs
	#https://healthyeater.com/how-to-calculate-your-macros
	#MALES: 10 x weight (kg) + 6.25 x height (cm) – 5 x age (y) + 5 = REE (Resting Energy Expenditure)
	def getMacros(self):
		inTakeCalories = Profile.getCalories(self)
		protein = self.weight * Decimal(2.2) * Decimal(0.8)
		fat = (inTakeCalories * Decimal(0.25))/ 9
		cals = inTakeCalories - (protein * 4) - (fat * 9)
		carbs = cals / 4
		macros={
			'Rasvaa: ' : round(fat,0),
			'Hiilihydraatteja: ' : round(carbs,0),
			'Proteiinia: ': round(protein,0)
			
		}
		return macros

	def getProfileRecipes(self):
		recipes = Recipe.objects.filter(author_id=self.user)
		return recipes

	def getFavoriteRecipes(self):
		favorites = FavoriteRecipes.objects.filter(user=self.user.id).all()
		favoriteRecipes = []
		for favorite in favorites:
			favoriteRecipes.append(favorite.favoriteRecipe)
		return favoriteRecipes

	def getSavedMealplans(self):
		mealplans = Mealplan.objects.filter(createdBy_id=self.user.id).all()
		savedMealplans = []
		for mealplan in mealplans:
			savedMealplans.append(mealplan)

		return savedMealplans

	def save(self, *args, **kwargs):
		# save profile macros to database if not set
		if self.weight:
			macros = self.getMacros()
			if not self.fats:
				self.fats = macros["Rasvaa: "]
			if not self.carbs:
				self.carbs = macros["Hiilihydraatteja: "]
			if not self.protein:
				self.protein = macros["Proteiinia: "]
		super(Profile,self).save()

class FavoriteRecipes(models.Model):
	favoriteRecipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
	user = models.ForeignKey(Profile, on_delete=models.CASCADE)


from unittest.util import _MAX_LENGTH
from django.db import models

# Create your models here.
class score_percentage(models.Model):
    category=models.CharField(max_length=50)
    season=models.CharField(max_length=50)
    score=models.IntegerField()

class roundrank_count_05_18(models.Model):
    rank=models.IntegerField()
    round1=models.IntegerField()
    round2=models.IntegerField()
    round3=models.IntegerField()
    round4=models.IntegerField()
    round5=models.IntegerField()
    round6=models.IntegerField()
    
class roundrank_count_18_22(models.Model):
    rank=models.IntegerField()
    round1=models.IntegerField()
    round2=models.IntegerField()
    round3=models.IntegerField()
    round4=models.IntegerField()
    round5=models.IntegerField()
    round6=models.IntegerField()
from django.db import models
from django.contrib.auth.models import User
from .selections import *

# Create your models here.

class AaUser(models.Model):
    user_name = models.OneToOneField(User, null=True,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    favorite_team = models.ForeignKey('AaTeams',db_column='favorite_team',related_name='favorite_team',on_delete = models.CASCADE,null=True,blank=True)
    euro_winner = models.CharField(max_length=20,choices=choices_teams,null=True,blank=True)
    golden_boot = models.CharField(max_length=40,choices=choices_gBoot,null=True,blank=True)
    golden_ball = models.CharField(max_length=40,choices=choices_gBall,null=True,blank=True)
    young_player = models.CharField(max_length=40,choices=choices_youngPlayer,null=True,blank=True)
    user_points = models.DecimalField(max_digits=10, decimal_places=3, default=0, blank=True,null=True)

    def __str__(self):
            return (str(self.user_name))

class AaTeams(models.Model):
    team_id = models.AutoField(auto_created=True,primary_key=True)
    team_name = models.CharField(max_length=20)
    team_group = models.CharField(max_length=1)
    team_odds = models.IntegerField(null=True,blank=True)

    def __str__(self):
            return (self.team_name)


class AaPlayers(models.Model):
    player_id = models.AutoField(auto_created=True,primary_key=True)
    player_name = models.CharField(max_length=30)
    player_team = models.ForeignKey('AaTeams',db_column='player_team',related_name='player_team',on_delete = models.CASCADE,null=True,blank=True)

    def __str__(self):
            return (self.player_name)


class AaMatches(models.Model):
    match_id = models.AutoField(auto_created=True,primary_key=True)
    group = models.CharField(max_length=1)
    team_1 = models.ForeignKey('AaTeams',db_column='team_1',related_name='team_1',on_delete = models.CASCADE)
    team_2 = models.ForeignKey('AaTeams',db_column='team_2',related_name='team_2',on_delete = models.CASCADE)
    matchday = models.IntegerField()
    score_1 = models.IntegerField(verbose_name='Score 1',blank=True,null = True)
    score_2 = models.IntegerField(verbose_name='Score 2',blank=True,null = True)
    match_datetime = models.DateTimeField()
    competetive = models.BooleanField(default=False, null=True)
    endtime = models.CharField(max_length=30,choices=choices_endtime,null=True,blank=True,default='Full-time')
    winner = models.ForeignKey('AaTeams',db_column='winner',on_delete=models.CASCADE,blank=True,null=True)


    def __str__(self):
            return (str(self.match_id))

class AaPredictions(models.Model):
    prediction_id = models.AutoField(auto_created=True,primary_key=True)
    user_id = models.ForeignKey('AaUser',on_delete=models.CASCADE)
    match_id = models.ForeignKey('AaMatches',on_delete=models.CASCADE)
    p_score1 = models.IntegerField(null=True,default=0)
    p_score2 = models.IntegerField(null=True,default=0)
    p_points = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True, default=0)
    p_computed = models.BooleanField(default=False,blank=True,null=True)
    p_endtime = models.CharField(max_length=30,null=True,choices=choices_endtime,blank=True,default='Full-time')
    p_winner = models.ForeignKey('AaTeams',db_column='winner',on_delete=models.CASCADE,blank=True,null=True)
    
    def __str__(self):
            return (str(self.user_id)+"_"+str(self.match_id))


from django.forms import ModelForm, HiddenInput, DateTimeInput, TextInput, Select, RadioSelect
from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']


class ProfileForm(ModelForm):
    class Meta:
        model = AaUser
        fields = '__all__'
        widgets = {
            'user_name':HiddenInput,
            'first_name':forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'}),
            'last_name':forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}),
            'favorite_team':Select(attrs={'class':'form-control','placeholder':'Favorite Team'}),
            'euro_winner':Select(attrs={'class':'form-control','placeholder':'Euro Winner'}),
            'golden_boot':Select(attrs={'class':'form-control','placeholder':'Golden Boot'}),
            'golden_ball':Select(attrs={'class':'form-control','placeholder':'Golden Ball'}),
            'young_player':Select(attrs={'class':'form-control','placeholder':'Young Player'}),
            'user_points':HiddenInput
            }

class PredictionForm(ModelForm):
 

    def clean(self):
        
        cleaned_data = super(PredictionForm,self).clean()
            
        score1 = cleaned_data.get('p_score1')
        score2 = cleaned_data.get('p_score2')
        endtime = cleaned_data.get('p_endtime')
        winner = cleaned_data.get('p_winner')
       

        if (endtime == None) :
            raise ValidationError('Pick whether match ends in 90 or not')

        if winner == None:
            raise ValidationError('Please pick a winner')
       
        if score1 == score2 and endtime == 'Full-time':
            raise ValidationError('How you predicting a draw in knockout and choosing Full-time')

        elif score1 != score2 and endtime != 'Full-time':
            raise ValidationError("How you predicting a winner in fulltime and choosing ET or PENS")

        if score1 != score2 and endtime == 'Full-time':
            if (score1 > score2) and winner == 'Turkey':
                raise ValidationError('cant be doing this homie')


        return cleaned_data

    class Meta:
        model = AaPredictions
        fields = ['p_score1','p_score2','p_endtime','p_winner']


        

        

    

        
        
            

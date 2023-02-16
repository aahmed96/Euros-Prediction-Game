from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import *
from django import forms
from django.forms import ValidationError
from .forms import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware
from datetime import timedelta, datetime, date, timezone
import time as ts
from .pointCalc import *
from django.db.models import Count, Sum, Aggregate
import pytz
from operator import itemgetter
from .redis import *


# Create your views here.
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method =='POST':
            form=CreateUserForm(request.POST)

            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')
                #group = Group.objects.get(name="cust")
                #user.groups.add(group)
                #AaCustomer.objects.create(
                #    user=user,
                #)
                messages.success(request,'Account was created for: ' + username)
                return redirect('login')

        context={"form":form}
        return render(request,'euros20/register.html',context)
    return HttpResponse('register')

def loginPage(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('homeNew'))
    else:
        if request.method =='POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request,username=username,password=password)

            if user is not None:
                login(request,user)
                return HttpResponseRedirect(reverse('homeNew'))
            else:
                messages.info(request,'Username OR password is incorrect')

        context={}
        return render(request,'euros20/login.html',context)

@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def password_reset(request):
    return HttpResponse('password reset')

@login_required(login_url='login')
def home(request):
    test_time = datetime.now()
    utc = pytz.utc
    time_now = utc.localize(datetime.now()) #localize current time
    users = AaUser.objects.all() #get all users
    matches = AaMatches.objects.all().order_by('match_datetime') #get all matches
    current_username = request.user #get current user

    if AaUser.objects.filter(user_name=current_username).exists() is False:
        current_user = AaUser.objects.create(user_name=current_username)
    else:
        current_user = AaUser.objects.get(user_name=current_username)

    userFullName = str(current_user.first_name+' '+current_user.last_name)

    picks = current_user

    # counter of the number of matches completed
    count_matches = 0

    #UPDATING TIME LEFT FOR EACH GAME
    timers = []
    for match in matches:

        time_left = round(((match.match_datetime - time_now).total_seconds())/3600)
        if time_left < 0:
            time_left = '-'
        time_left = [match.match_id,time_left]
        timers.append(time_left)

        if match.score_1 is not None:
            count_matches += 1

    # before computing, check if there is redis entry for point calculations
    redis_key = get_redis_matches_key(count_matches)
    redis_leaderboard_data = get_leaderboard_from_redis(redis_key)



    # CHECK REDIS BEFORE COMPUTING
    if redis_leaderboard_data is None:
        predictions_calculations = {}
        #UPDATING EVERYONES PREDICTIONS
        for user in users:
            if AaPredictions.objects.filter(user_id = user).exists():
                predictions = AaPredictions.objects.filter(user_id = user,p_computed=False)
                sum_points = 0
                for match in matches:

                    if not match.score_1 is None and predictions.filter(match_id=match.match_id).exists() is True:
                        prediction = predictions.get(match_id=match.match_id)
                        score_1 = match.score_1
                        score_2 = match.score_2
                        a_endtime = match.endtime
                        a_winner = match.winner
                        competetive = match.competetive

                        p_score1 = prediction.p_score1
                        p_score2 = prediction.p_score2
                        p_endtime = prediction.p_endtime
                        p_winner = prediction.p_winner


                        if prediction.p_score1 is not None: #ensures that user has made prediciton
                            pts = computePoints(score_1,score_2,p_score1,p_score2,
                            a_endtime,p_endtime,a_winner,p_winner)
                            prediction.p_computed = True #set this to true
                            prediction.p_points = float(pts)
                            sum_points += float(pts)
                            prediction.save()

    leaderboard = []

    if AaPredictions.objects.filter(user_id = current_user).exists():
        predictions = AaPredictions.objects.filter(user_id = current_user).order_by('-match_id')

        if redis_leaderboard_data is not None:
            for user_id, values in redis_leaderboard_data.items():
                values = values.split("=")
                user_board = [user_id,values[0],int(values[1])]
                leaderboard.append(user_board)
            leaderboard = sorted(leaderboard,key = itemgetter(2),reverse=True)
        else:
            leaderboardcache = {}
            all_predictions = AaPredictions.objects.values('user_id').annotate(Sum('p_points'))
            #assigning leaderboard values
            for user_predictions in all_predictions:
                user_predictions = list(user_predictions.values())
                print(user_predictions)
                user_id = user_predictions[0]
                if user_predictions[1] is not None:
                    user_pts = float(user_predictions[1])
                else:
                    user_pts = '-'
                name = list((users.filter(pk=user_id).values('first_name','last_name'))[0].values())
                full_name = str(name[0]+' '+name[1])
                user_board = [user_id,full_name,user_pts]
                leaderboard.append(user_board)
                leaderboardcache[user_id] = full_name+"="+str(int(user_pts))
            leaderboard = sorted(leaderboard,key = itemgetter(2),reverse=True)
            write_leaderboard_to_redis(redis_key,leaderboardcache)

    else:
        predictions = None

    return render(request, 'euros20/home.html',context={
        'picks':picks,
        'matches':matches,
        'predictions': predictions,
        'leaderboard': leaderboard,
        'time_now': time_now,
        'userFullName': userFullName,
        'timers':timers})

@login_required(login_url='login')
def homeNew(request):
    test_time = datetime.now()
    utc = pytz.utc
    time_now = utc.localize(datetime.now()) #localize current time
    
    predictions = AaPredictions.objects.all()
    matches = AaMatches.objects.all().order_by('match_datetime') #get all matches
    current_username = request.user #get current user

    if AaUser.objects.filter(user_name=current_username).exists() is False:
        current_user = AaUser.objects.create(user_name=current_username)
    else:
        current_user = AaUser.objects.get(user_name=current_username)

    userFullName = str(current_user.first_name+' '+current_user.last_name)
    picks = current_user


    #get user specific predictions
    if AaPredictions.objects.filter(user_id = current_user).exists():
        user_predictions = AaPredictions.objects.filter(user_id = current_user).order_by('-match_id')

    counter = 0

    #timer computations
    timers = []
    for match in matches:

        time_left = round(((match.match_datetime - time_now).total_seconds())/3600)
        if time_left < 0:
            time_left = '-'
        time_left = [match.match_id,time_left]
        timers.append(time_left)
    
    #computing points
    for prediction in predictions:
        #here we compute points
        if (prediction.p_computed is False) and (prediction.match_id.score_1 is not None):

            #get actual scores 
            score_1 = prediction.match_id.score_1
            score_2 = prediction.match_id.score_2
            a_endtime = prediction.match_id.endtime
            a_winner = prediction.match_id.winner
            
            #get predictions
            p_score1 = prediction.p_score1
            p_score2 = prediction.p_score2
            p_endtime = prediction.p_endtime
            p_winner = prediction.p_winner

            #check whether user has made a valid prediction
            if prediction.p_score1 is not None and prediction.p_winner is not None: 
                pts = computePoints(score_1,score_2,p_score1,p_score2,
                a_endtime,p_endtime,a_winner,p_winner)
                prediction.p_computed = True #set this to true
                prediction.p_points = float(2*float(pts))
                #sum_points += float(pts)
                prediction.save()
    
    #leaderboard 
    leaderboard = []
    predictions = predictions.values('user_id','user_id__first_name','user_id__last_name','user_id__user_points').annotate(Sum('p_points'))
    for prediction in predictions:
        prediction = list(prediction.values())
        outright = int(prediction[3])
        print(outright)
        #print(prediction[0],prediction[1],prediction[2],prediction[3])
        name = str(str(prediction[1])+' '+str(prediction[2]))
        points = round(prediction[4]+outright)
        
        entry = [name,points]
        leaderboard.append(entry)
        #print(name,points)
    
    leaderboard = sorted(leaderboard,key = itemgetter(1),reverse=True)
    
    context = {
        'leaderboard':leaderboard,
        'matches':matches,
        'predictions':user_predictions,
        'timers':timers,
        'time_now':time_now,
        'picks':picks,
        'userFullName': userFullName
    }

    return render(request,'euros20/homeNew.html',context=context)


@login_required(login_url='login')
def predict(request,pk):
    
    utc = pytz.utc
    current_match = AaMatches.objects.get(pk=pk)
    if utc.localize(datetime.now()) > current_match.match_datetime:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    current_username = request.user
    current_user = AaUser.objects.get(user_name=current_username)

    if AaPredictions.objects.filter(user_id = current_user,match_id = current_match).exists() is False:
        current_prediction = AaPredictions.objects.create(user_id=current_user,match_id=current_match)
    else:
        current_prediction = AaPredictions.objects.get(user_id=current_user,match_id=current_match)


    Prediction_Form = PredictionForm(instance = current_prediction)
    
    #add functionality to check whether draw or not
    
    Prediction_Form.fields['p_winner'].queryset = AaTeams.objects.filter(
        team_name=current_match.team_1) | AaTeams.objects.filter(team_name=current_match.team_2)

    if request.method == 'POST':
        Prediction_Form = PredictionForm(request.POST,instance=current_prediction)
        Prediction_Form.fields['p_winner'].queryset = AaTeams.objects.filter(
        team_name=current_match.team_1) | AaTeams.objects.filter(team_name=current_match.team_2)

        

        if Prediction_Form.is_valid():
            cleaned_data = Prediction_Form.cleaned_data
            p_score1 = cleaned_data['p_score1']
            p_score2 = cleaned_data['p_score2']
            endtime= cleaned_data['p_endtime']
            winner = cleaned_data['p_winner']

            current_match.team_1
            current_match.team_2
            if endtime == 'Full-time':

                if (p_score1 > p_score2) and (winner==current_match.team_2):
                    messages.info(request,'Cant be doing this homie')
                elif (p_score1 < p_score2) and (winner==current_match.team_1):
                    messages.info(request,'Cant be doing this homie')

                else:
                    Prediction_Form.save()
                    time = datetime.now()
                    ts.sleep(0.2) # force a delay for fresh data
                    return redirect('homeNew')
            else:
                Prediction_Form.save()
                time = datetime.now()
                ts.sleep(0.2) # force a delay for fresh data
                return redirect('homeNew')

                
        
    context = {
        'Prediction_Form':Prediction_Form,
        'match':current_match
    }

    return render(request,'euros20/predict.html',context = context)

@login_required(login_url='login')
def profile(request):
    utc = pytz.utc
    start_time = utc.localize(datetime(2021,6,11,19,0,0))

    time_now = utc.localize(datetime.now())

    if time_now > start_time:
        return redirect('home')
    else:
        current_user = request.user
        # current_user = AaUser.objects.create(user_name=request.user)
        if AaUser.objects.filter(user_name=current_user).exists() is False:
            current_user = AaUser.objects.create(user_name=request.user)
        else:
            current_user = AaUser.objects.get(user_name=request.user)

        #current_user is the entry in the table which we can manipulate

        Profile_Form = ProfileForm(instance=current_user)
        if request.method == 'POST':
            Profile_Form = ProfileForm(request.POST,instance=current_user)
            if Profile_Form.is_valid:
                Profile_Form.save()
                return redirect('profile')

        context = {"Profile_Form":Profile_Form}


        return render(request, 'euros20/profile.html',context)

@login_required(login_url='login')
def randr(request):

    return render(request,'euros20/randr.html')

@login_required(login_url='login')
def past(request):
    current_user = AaUser.objects.get(user_name=request.user)
    userID = current_user.pk
    utc = pytz.utc
    matches = AaMatches.objects.all().order_by('-match_datetime')
    time_now = utc.localize(datetime.now())
    m_preds = [] #storing all the matches with predictions

    for match in matches:
        if match.match_datetime < time_now:
            match_predictions = AaPredictions.objects.filter(match_id=match.match_id).order_by('-p_points','user_id__first_name')
            m_preds.append(match_predictions)


    context = {"matches":matches,
                'userID':userID,
                "m_preds":m_preds,}

    return render(request,'euros20/past.html',context)


@login_required(login_url='login')
def pastPredict(request,pk):
    current_user = AaUser.objects.get(user_name=request.user)
    match = AaMatches.objects.get(match_id=pk)

    if match.matchday <3.1:
    
    #color code the winner
        if match.score_1 is not None:
            actual = result_calc(match.score_1,match.score_2)
            dictResult = {'team A':1,'draw':2,'team B':3}
            actual = dictResult[actual]
            actual_result = str(str(match.score_1)+'-'+str(match.score_2))
        else:
            actual = None
            actual_result = None
        

        predictions = AaPredictions.objects.filter(match_id=pk).order_by('-p_points','user_id__first_name')
        

        team_A = 0
        team_B = 0
        draw = 0

        scores = {}

        #TIME TO DO SOME MATH
        for prediction in predictions:
            outcome = result_calc(prediction.p_score1,prediction.p_score2)
            score = str(str(prediction.p_score1)+'-'+str(prediction.p_score2))
            
            if score not in scores:
                scores[score] = 1
            else:
                scores[score]+=1

            if outcome == 'team A':
                team_A +=1
            elif outcome == 'team B':
                team_B+=1
            else:
                draw+=1

        results = [team_A,draw,team_B]
        
        #lets sort scores
        
        scores = sorted(scores.items(),key=lambda x: x[1],reverse=True)
        
        context = {
            "predictions":predictions,
            "match":match,
            "results":results,
            "scores":scores,
            "actual":actual,
            "actual_result":actual_result,
            "current_user":current_user   
        }

        return render(request,'euros20/pastPredict.html',context)

    #match 
    else:
        #color code the winner
        if match.score_1 is not None:
            if match.winner == match.team_1:
                actual = 1
            else:
                actual = 2

            #this is the full-time score
            actual_result = str(str(match.score_1)+'-'+str(match.score_2))

            a_endtime = match.endtime
            if a_endtime == 'Full-time':
                end = 1
            elif a_endtime == 'Extra-time':
                end = 2
            else:
                end = 3
        else:
            actual = None
            actual_result = None
            end = None
        

        predictions = AaPredictions.objects.filter(match_id=pk).order_by('-p_points','user_id__first_name')
        
        #counting teams
        team_A = 0
        team_B = 0

        #counting end-times
        Full_time = 0
        Extra_time = 0
        Penalties = 0
        

        scores = {}

        #TIME TO DO SOME MATH
        for prediction in predictions:
            outcome = prediction.p_winner
            endtime = prediction.p_endtime
            score = str(str(prediction.p_score1)+'-'+str(prediction.p_score2))
            
            if score not in scores:
                scores[score] = 1
            else:
                scores[score]+=1
            
            if outcome == match.team_1:
                team_A +=1
            elif outcome == match.team_2:
                team_B+=1
            
            if endtime == 'Full-time':
                Full_time+=1
            elif endtime == 'Penalties':
                Penalties+=1
            else:
                Extra_time+=1
            

        results = [team_A,team_B]
        endtimes = [Full_time,Extra_time,Penalties]
        
        #lets sort scores
        
        scores = sorted(scores.items(),key=lambda x: x[1],reverse=True)
        
        context = {
            "predictions":predictions,
            "match":match,
            "results":results,
            "scores":scores,
            "actual":actual,
            "actual_result":actual_result,
            "current_user":current_user,
            "endtimes":endtimes,
            "end":end
        }

        return render(request,'euros20/pastPredictKO.html',context)

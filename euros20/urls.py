from django.urls import path
from . import views

urlpatterns = [
    path('',views.loginPage,name='login'),
    path('register',views.register,name='register'),
    path("logout",views.logoutUser,name="logout"),
    #path('reset',views.password_reset),
    #path('home',views.home,name='home'),
    #path('profile',views.profile,name='profile'),
    path("predict/<str:pk>",views.predict, name="predict"),
    path("randr",views.randr, name='randr'),
    #path("past",views.past, name='past'),
    path("pastPredict/<str:pk>",views.pastPredict, name="pastPredict"),
    path("pastPredictKO/<str:pk>",views.pastPredict, name="pastPredictKO"),
    path("homeNew",views.homeNew, name='homeNew')
    



]


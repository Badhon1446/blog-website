from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='home'),    
    path('post/create',views.post_create, name='post_create'),
    path('post_list',views.post_list,name='post_list'),
    path('post/details/<int:id>',views.post_details,name='post_details'),
    path('post/update/<int:id>',views.post_update, name='post_update'),
    path('post/delete<int:id>',views.post_delete,name='post_delete'),
    path('post/<int:id>/like',views.like_post,name='like_post'),
    path('profile',views.profile,name='profile'),
    path('login',views.login_view,name='login'),
    path('register',views.signup_view,name='register'),
    path('logout',views.logout_view,name='logout'),
]

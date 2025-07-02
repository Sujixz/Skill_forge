from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('course_detail/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/', views.courses, name='courses'),
    path('checkout/<int:course_id>/', views.checkout, name='checkout'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('enrolled_courses/', views.enrolled_courses, name='enrolled_courses'),
    path('course_content/<int:course_id>/', views.course_content, name='course_content'),





 
    path("signup/", views.signup, name="signup"),
    path("signin/", views.signin, name="signin"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('search_results/', views.search_results, name='search_results'),
    path("userlogout/", views.userlogout, name="userlogout"),

]    
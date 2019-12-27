from django.urls import path
from .views import index, other_page
from .views import profile
from .views import BBLogoutView
from .views import ChangeUserInfoView
from .views import BBPasswordChangeView
from .views import RegisterDoneView
from .views import RegisterUserView
from .views import user_activate
from .views import DeleteUserView
from .views import BBPasswordResetView
from .views import BBPasswordResetConfirmView
from .views import by_rubric
from .views import detail
from .views import profile_bb_add, profile_bb_detail, profile_bb_change, profile_bb_delete
from .views import login
from .views import comment_change
from .views import comment_add_answer
from .views import answer_change


app_name = 'main'
urlpatterns = [
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('accounts/logout/', BBLogoutView.as_view(), name='logout'),
    path('accounts/profile/change/<int:pk>/', profile_bb_change, name='profile_bb_change'),
    path('accounts/profile/delete/<int:pk>/', profile_bb_delete, name='profile_bb_delete'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/profile/add/', profile_bb_add, name='profile_bb_add'),
    path('accounts/profile/<int:pk>/', profile_bb_detail, name='profile_bb_detail'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/login/', login, name='login'),
    path('accounts/password/change/', BBPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password/reset/<uidb64>/<token>/', BBPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('accounts/password/reset/', BBPasswordResetView.as_view(), name='password_reset'),
    path('comment/change/<int:comment_id>/', comment_change, name='comment_change'),
    path('comment/add_answer/<int:comment_id>/', comment_add_answer, name='comment_add_answer'),
    path('answer/change/<int:answer_id>/', answer_change, name='answer_change'),
    path('<int:rubric_pk>/<int:pk>/', detail, name='detail'),
    path('<int:pk>/', by_rubric, name='by_rubric'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),
]

from django.urls import path

from main.views import index, other_page, BbLoginView, profile, BbLogoutView, ChangeUserInfoView, BbPasswordChangeView, \
    RegisterDoneView, RegisterUserView, user_activate, DeleteUserView, by_rubric, detail, profile_bb_detail, \
    profile_bb_add, BbUpdateView, BbDeleteView, likes_dislikes, complain

app_name = 'main'

urlpatterns = [
    path('accounts/login/', BbLoginView.as_view(), name='login'),
    path('accounts/logout/', BbLogoutView.as_view(), name='logout'),
    # path('accounts/profile/<int:pk/>', profile_bb_detail, name='profile_bb_detail'),
    path('accounts/profile/change/', ChangeUserInfoView.as_view(), name='profile_change'),
    path('accounts/password/change/', BbPasswordChangeView.as_view(), name='password_change'),
    path('accounts/profile/add/', profile_bb_add, name='profile_bb_add'),
    path('accounts/profile/update/<int:pk>/', BbUpdateView.as_view(), name='profile_bb_update'),
    path('accounts/profile/deletebb/<int:pk>/', BbDeleteView.as_view(), name='profile_bb_delete'),
    path('accounts/profile/delete/', DeleteUserView.as_view(), name='profile_delete'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/register/activate/<str:sign>/', user_activate, name='register_activate'),
    path('accounts/register/done/', RegisterDoneView.as_view(), name='register_done'),
    path('accounts/register/', RegisterUserView.as_view(), name='register'),
    path('<int:rubric_pk>/<int:pk>/', detail, name='detail'),
    path('likes/<str:choice>/<int:pk>/', likes_dislikes, name='likes_dislikes'),
    path('<int:pk>/', by_rubric, name='by_rubric'),
    path('<str:page>/', other_page, name='other'),
    path('comment/<int:rubric_pk>/<int:pk>/<int:comment_pk>/', detail, name='comment'),
    path('complain/<int:pk>/', complain, name='complain'),
    path('', index, name='index'),
]

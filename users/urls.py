from django.contrib import admin
from django.urls import path
from .views import RegisterView, OrganisationListView, LoginView ,UserDetailView 
from .views import UserView,LogoutView, OrganisationsView,OrganisationDetailView,CreateOrganisationView,AddUserToOrganisationView

urlpatterns = [
    path("auth/register", RegisterView.as_view()),
    path("auth/login", LoginView.as_view()),
    path('api/users', UserView.as_view()),
    path('api/organisations/str:orgId', OrganisationDetailView.as_view()),#todo
    path('api/organisation', CreateOrganisationView.as_view(), name='create_organisation'),
    path("api/organisations", OrganisationsView.as_view()),
    path('api/organisations/str:orgId/users', AddUserToOrganisationView.as_view(), name='add_user_to_organisation'),
    path('api/users/str:id', UserDetailView.as_view(), name='user_detail'),

    path("api/organisationList", OrganisationListView.as_view()),#todo
    path('logout', LogoutView.as_view()),
] 
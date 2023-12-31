# from django.contrib.auth.views import LoginView
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    get_cookie_view,
    set_cookie_view,
    get_session_view,
    set_session_view,
    # logout_view,
    MyLogoutView,
    MyLoginView,
    AboutMeView,
    RegisterView,
    FooBarView,
    change_profile,
    change_photo,
    PhotoUpdateView,
    ProfilesListView,
    ProfileDetailsView,
    HelloView,

)

app_name = 'myauth'

urlpatterns = [
    # path(
    #     'login/',
    #     LoginView.as_view(
    #         template_name="myauth/login.html",
    #         redirect_authenticated_user=True,
    #     ),
    #     name="login",
    # ),
    path("login/", MyLoginView.as_view(), name="login"),
    path("hello/", HelloView.as_view(), name="hello"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),

    path("register", RegisterView.as_view(), name="register"),

    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("cookie/set/", set_cookie_view, name="cookie-set"),

    path("session/get/", get_session_view, name="session-get"),
    path("session/set/", set_session_view, name="session-set"),

    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),

    path("change-profile/", change_profile, name='change-profile'),
    path("about-me/change-photo/", change_photo, name='change-photo-me'),
    path("change-photo/profile/<int:pk>", PhotoUpdateView.as_view(), name='change-photo'),

    path("profiles/", ProfilesListView.as_view(), name="profiles_list"),
    path("profiles/<int:pk>/", ProfileDetailsView.as_view(), name="profile_details"),

]

if settings.DEBUG:
    urlpatterns.extend(
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
    urlpatterns.extend(
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )

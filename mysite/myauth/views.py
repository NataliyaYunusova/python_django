from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import CreateView, TemplateView, ListView, DetailView, UpdateView
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView, LoginView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.views import View
from django.utils.translation import gettext_lazy as _, ngettext

from .models import Profile
from .forms import ProfileForm, UserForm, ProfileAvatarForm

import logging

logger = logging.getLogger(__name__)


class HelloView(View):
    welcome_message = _("welcome hello world")

    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{products_line}</h2>"

        )


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"
    model = Profile

# class AboutMeView(UpdateView):
#     model = Profile
#     fields = ['avatar']
#     template_name = "myauth/about-me.html"
#
#     def get_success_url(self):
#         return reverse_lazy('myauth:about-me')
#
#     def get_object(self, queryset=None):
#         return self.request.user.profile


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password
        )
        login(request=self.request, user=user)
        return response


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/admin/")
        return render(request, "myauth/login.html")

    username = request.POST["username"]

    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("/admin/")
    return render(request, "myauth/login.html", {"error": "Invalid login credentials"})


class MyLoginView(LoginView):
    template_name = "myauth/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        logger.info(f'Пользователь {username} успешно аутентифицирован')
        return super().form_valid(form)

    def form_invalid(self, form):
        username = form.data.get('username')
        logger.warning(f'Неудачная попытка аутентификации пользователя {username}')
        return super().form_invalid(form)


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse("myauth:login"))


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")

    def dispatch(self, request, *args, **kwargs):
        logger.info(f'Пользователь {request.user.username} вышел из системы')
        response = super().dispatch(request, *args, **kwargs)
        return response


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:

    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})


@login_required
def change_profile(request):
    if request.method == 'POST':
        user_form = UserForm(data=request.POST, instance=request.user)
        profile_form = ProfileForm(data=request.POST, instance=request.user.profile, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
        return redirect('myauth:about-me')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'myauth/change-profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def change_photo(request):
    if request.method == 'POST':
        profile_avatar_form = ProfileAvatarForm(data=request.POST, files=request.FILES, instance=request.user.profile)
        if profile_avatar_form.is_valid():
            profile_avatar_form.save()
        return redirect('myauth:about-me')
    else:
        profile_avatar_form = ProfileAvatarForm(instance=request.user.profile)
    return render(request, 'myauth/change-photo-me.html', {
        'profile_avatar_form': profile_avatar_form
    })


class PhotoUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileAvatarForm
    template_name = "myauth/change-photo.html"

    def get_success_url(self):
        return reverse_lazy('myauth:profile_details', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        pk = self.kwargs.get("pk")
        user_profile = get_object_or_404(Profile, pk=pk)
        return user_profile


class ProfilesListView(ListView):
    template_name = "myauth/profiles_list.html"
    context_object_name = "profiles"
    queryset = Profile.objects.all()


class ProfileDetailsView(DetailView):
    model = Profile
    template_name = "myauth/profile_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProfileForm(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        profile = self.get_object()
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("myauth/profile_details.html")
        else:
            return self.render_to_response(self.get_context_data(form=form))

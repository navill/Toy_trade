import json
import ast
from django.contrib.auth.views import LoginView as DefaultLoginView, LogoutView as DefaultLogoutView
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, resolve_url

# Create your views here.
from django.urls import reverse
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.base import View

from accounts.forms import UserProfileForm, LoginForm
from accounts.models import UserProfile
from location.models import UserSession

from location.signals import user_logged_in
from location.utils import get_client_ip
from notification.models import Action
from products.models import Product, Comment


class Home(View):
    action_qs = Action.objects.filter(check=False)
    temp_value = None

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # 내 게시글에 대해 누군가가 댓글 작성 시 알림
            queryset = self.action_qs
            user = request.user
            # 나를 제외하고 내가 쓴 게시글의 모든 댓글
            comments = Comment.objects.exclude(user=user).filter(product__user=user)
            ids = [c.id for c in comments]
            # 앞에서 필터링된 모든 Comment의 Action
            comment_actions = queryset.by_model(Comment)
            comment_actions = comment_actions.filter(object_id__in=ids).order_by('-created')

            self.temp_value = 'a'
            context = {
                'comment_actions': comment_actions
            }
            return render(request, 'home.html', context=context)
        else:
            return redirect('login')

    def post(self, request, *args, **kwargs):
        is_checked = request.POST.get('check')
        # print(is_checked)  -> True
        actions_from_templates = request.POST.get('actions')

        print('post actions: ', actions_from_templates)
        if is_checked:
            actions = self.action_qs.by_model(Comment)
            for action in actions:
                action.check = True
            Action.objects.bulk_update(actions, ['check'])
        return redirect('home')


class UserProfileDetailView(DetailView):
    template_name = 'accounts/profile_detail.html'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        # 인증 확인
        if self.request.user.is_authenticated:
            user = self.request.user
            # 접근자와 프로필 유저가 동일한지 확인
            if username == user.username:
                # qs = UserProfile.objects.filter(user=user).user()
                obj, created = UserProfile.objects.with_user().get_or_create(user=user)
                return obj
            raise Http404
        raise Http404

    def get(self, request, *args, **kwargs):
        # 내 게시물을 제외한 모든 게시물 등록 확인
        # actions = Action.objects.exclude(user=request.user).by_model(Product)
        # print(actions)  # -> 나를 제외한 사람들이 생성한 Product objects

        # 내 게시글에 대해 누군가가 댓글 등록
        qs = Action.objects.all()
        user = request.user
        reply_qs = qs.exclude(user=user).by_model(Comment, model_queryset=True).select_related('product').filter(
            product__user=user)
        user_profile = self.get_object()

        # 내 위치와 동일한 유저의 댓글
        if user_profile.filtered_city:
            replies = reply_qs.filter(user__userprofile__city=user.userprofile.city)
        else:
            replies = reply_qs
        # 프로필 업데이트 정보
        my_info = qs.filter(user=request.user).by_model(UserProfile)[:4]

        # 내 위치 정보
        ip = get_client_ip()
        user_session = UserSession.objects.filter(Q(user=user) & Q(ip_address=ip)).first()
        coord = ast.literal_eval(user_session.city_data)
        lat = coord['lat']
        lng = coord['long']

        coordinates = f'lat: {lat}, lng: {lng}'
        context = {
            'object': self.get_object(),
            'my_info': my_info,
            'replies': replies,
            'coordinates': coordinates,
        }
        return render(request, 'accounts/profile_detail.html', context=context)


class LoginView(DefaultLoginView):
    form_class = LoginForm
    template_name = 'account/login.html'

    def form_valid(self, form):
        form_ = super().form_valid(form)
        if self.request.user.is_authenticated:
            user_logged_in.send(self.request.user, request=self.request)
            # print(self.request.session.items())
        return form_


class LogoutView(DefaultLogoutView):
    pass


class UserProfileUpdateView(UpdateView):
    template_name = 'accounts/profile_update.html'
    form_class = UserProfileForm

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        # 인증 확인
        if self.request.user.is_authenticated:
            user = self.request.user
            # 접근자와 프로필 유저가 동일한지 확인
            if username == user.username:
                qs = UserProfile.objects.filter(user=user)
                if qs.exists():
                    obj = qs.first()

                    return obj
                else:
                    raise Http404
        raise Http404

    def get_success_url(self):
        user = self.request.user
        return reverse("accounts:detail", kwargs={'username': user})

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.save()
        return super().post(request, *args, **kwargs)

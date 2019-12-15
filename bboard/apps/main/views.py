from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render_to_response

from django.conf import settings

from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect

from django.template import TemplateDoesNotExist
from django.template import RequestContext
from django.template.loader import get_template

from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetConfirmView

from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView

from django.core.signing import BadSignature
from django.core.paginator import Paginator

from django.urls import reverse_lazy

from django.db.models import Q

from .models import AdvUser
from .models import SubRubric, Bb
from .models import Comment
from .forms import SearchForm
from .forms import ChangeInfoForm
from .forms import RegisterUserForm
from .forms import PasswordResetUserForm
from .forms import PasswordResetConfirmUserForm
from .forms import BbForm, AIFormSet
from .forms import UserCommentForm, GuestCommentForm
from .forms import LoginUserForm
from .forms import CommentChangeForm
from .utilities import signer, remember_user


def index(request):
    bbs = Bb.objects.all()[:10]

    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1

    paginator = Paginator(bbs, 2)
    page = paginator.get_page(page_num)

    context = {'bbs': bbs, 'page': page}

    return render(request, 'main/index.html', context)


def by_rubric(request, pk):
    rubric = get_object_or_404(SubRubric, pk=pk)
    bbs = Bb.objects.filter(rubric=pk)

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        q = Q(title__icontains=keyword) | Q(content__icontains=keyword)
        bbs = bbs.filter(q)
    else:
        keyword = ''

    form = SearchForm(initial={'keyword': keyword})
    paginator = Paginator(bbs, 2)

    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1

    page = paginator.get_page(page_num)
    context = {'rubric': rubric, 'page': page, 'bbs': page.object_list,
               'form': form}

    return render(request, 'main/by_rubric.html', context)


def detail(request, rubric_pk, pk):
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additionalimage_set.all()
    comments = Comment.objects.filter(bb=pk, is_active=True)
    initial = {'bb': bb.pk}
    form_class = ''
    form = ''

    if request.user.is_authenticated:
        form_class = UserCommentForm
        initial['author'] = request.user.pk
        form = form_class(initial=initial)
    else:
        form_class = GuestCommentForm
    form_class = UserCommentForm
    form = form_class(initial=initial)

    if request.method == 'POST':
        if 'delete' not in request.POST:
            c_form = form_class(request.POST)

            if c_form.is_valid():

                c_form.save()
                messages.add_message(request, messages.SUCCESS,
                                     'Комментарий добавлен!')
            else:
                form = c_form
                messages.add_message(request, messages.WARNING,
                                     'Комментарий не добавлен!')
        else:
            if request.user.is_authenticated:
                comment_pk = request.POST['comment_id']
                comment = Comment.objects.get(pk=comment_pk)

                comment.delete()

    context = {'bb': bb, 'ais': ais, 'comments': comments, 'form': form}

    return render(request, 'main/detail.html', context)


def other_page(request, page):
    try:
        template = get_template('main/' + page + '.html')
    except TemplateDoesNotExist:
        raise Http404
    return HttpResponse(template.render(request=request))


# Profile views -----------------------------------------------------------------
@login_required
def profile(request):
    bbs = Bb.objects.filter(author=request.user.pk)
    context = {'bbs': bbs}

    return render(request, 'main/profile.html', context)


@login_required
def profile_bb_detail(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additionalimage_set.all()
    comments = Comment.objects.filter(bb=pk, is_active=True)
    initial = {'bb': bb.pk}

    if request.user.is_authenticated:
        initial['author'] = request.user.username
        form_class = UserCommentForm
    else:
        form_class = GuestCommentForm

    form = form_class(initial=initial)

    if request.method == 'POST':
        c_form = form_class(request.POST)

        if c_form.is_valid():
            c_form.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Комментарий добавлен!')
        else:
            form = c_form
            messages.add_message(request, messages.WARNING,
                                 'Комментарий не добавлен!')

    context = {'bb': bb, 'ais': ais, 'comments': comments, 'form': form}

    return render(request, 'main/profile_bb_detail.html', context)


@login_required
def profile_bb_add(request):
    if request.method == "POST":
        form = BbForm(request.POST, request.FILES)

        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)

            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление добавлено!')

                return redirect('main:profile')
    else:
        form = BbForm(initial={'author': request.user.pk})
        formset = AIFormSet()

    context = {'form': form, 'formset': formset}

    return render(request, 'main/profile_bb_add.html', context)


@login_required
def profile_bb_change(request, pk):
    bb = get_object_or_404(Bb, pk=pk)

    if request.method == 'POST':
        form = BbForm(request.POST, request.FILES, instance=bb)

        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)

            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление изменено!')

                return redirect('main:profile')
    else:
        form = BbForm(instance=bb)
        formset = AIFormSet(instance=bb)
        context = {'form': form, 'formset': formset}

        return render(request, 'main/profile_bb_change.html', context)


@login_required
def profile_bb_delete(request, pk):
    bb = get_object_or_404(Bb, pk=pk)

    if request.method == 'POST':
        bb.delete()
        messages.add_message(request, messages.SUCCESS, 'Объявление удалено!')

        return redirect('main:profile')
    else:
        context = {'bb': bb}

        return render(request, 'main/profile_bb_delete.html', context)
# -----------------------------------------------------------------------------


# Login, Auth, User views -----------------------------------------------------
def login(request, template_name='registration/login.html',
          authentication_form=LoginUserForm):
    if request.method == 'POST':
        form = LoginUserForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']
            user = authenticate(username=username, password=password)

            if user:
                auth_login(request, user)

                if not remember_me:
                    context = {'form': form}
                    response = render(request, 'main/login.html', context)

                    # keys = [key for key in request.session.keys()]
                    # request.session[keys[0]].set_expiry(0)
                    # ['_auth_user_id', '_auth_user_backend', '_auth_user_hash']
                    # request.session['_auth_user_id'].set_expiry(0)
                    request.session.set_expiry(0)

                    # settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = True

                    return HttpResponseRedirect(reverse_lazy('main:index'))
                else:
                    return HttpResponseRedirect(reverse_lazy('main:profile'))
            else:
                form = LoginUserForm()
                context = {'form': form}

                return render(request, 'main/login.html', context)
        else:
            form = LoginUserForm()
            context = {'form': form}

            return render(request, 'main/login.html', context)
    else:
        form = LoginUserForm()
        context = {'form': form}

        return render(request, 'main/login.html', context)
    # if request.method == "POST":
    #     form = authentication_form(data=request.POST)
    #     if form.is_valid():
    #         if not form.cleaned_data.get('remember_me'):
    #             request.session.set_expiry(0)
    #
    #         auth_login(request, form.get_user())
    #
    #         if request.session.test_cookie_worked():
    #             request.session.delete_test_cookie()
    #
    #         return HttpResponseRedirect('main:profile')
    # else:
    #     form = authentication_form(request)
    #
    # request.session.set_test_cookie()
    # context = {'form': form}
    #
    # return render_to_response('main/login.html', context)


class BBLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    template_name = 'main/change_user_info.html'
    form_class = ChangeInfoForm
    success_url = reverse_lazy('main:profile')
    success_message = 'Личные данные пользователя изменены'

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin, PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя изменен'


class BBPasswordResetView(PasswordResetView):
    template_name = 'main/password_reset.html'
    success_url = reverse_lazy('main: index')
    subject_template_name = 'email/reset_password_letter_subject.txt'
    email_template_name = 'email/reset_password_letter_body.txt'
    form_class = PasswordResetUserForm


class BBPasswordResetConfirmView(LoginRequiredMixin, PasswordResetConfirmView):
    template_name = 'main/password_reset_confirm.html'
    success_url = reverse_lazy('main: login')
    form_class = PasswordResetConfirmUserForm


class RegisterUserView(CreateView):
    model = AdvUser
    template_name = 'main/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('main:register_done')


class RegisterDoneView(TemplateView):
    template_name = 'main/register_done.html'


def user_activate(request, sign):
    try:
        username = signer.unsign(sign)
    except BadSignature:
        return render(request, 'main/bad_signature.html')

    user = get_object_or_404(AdvUser, username=username)

    if user.is_activated:
        template = 'main/user_is_activated.html'
    else:
        template = 'main/activation_done.html'
        user.is_active = True
        user.is_activated = True
        user.save()
    return render(request, template)


class DeleteUserView(LoginRequiredMixin, DeleteView):
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удален')
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)
# ----------------------------------------------------------------------------


# Comments views
@login_required
def comment_change(request, comment_id):
    comment = Comment.objects.get(pk=comment_id)
    initial = {'bb': comment.bb, 'author': comment.author}
    form = CommentChangeForm(initial=initial)

    if request.method == 'POST':
        if request.user == comment.author:
            c_form = CommentChangeForm(request.POST)

            if c_form.is_valid():
                comment.content = request.POST['content']
                comment.save()

                messages.add_message(request, messages.SUCCESS,
                                        'Сообщение изменено!')

                return redirect('main:index')
            else:
                form = c_form

                messages.add_message(request, messages.WARNING,
                                     'Сообщение не изменено!')

    context = {'form': form, 'comment': comment, }

    return render(request, 'main/comment_change.html', context)


@login_required
def comment_add_answer(request, comment_id):
    comment = Comment.objects.get(pk=comment_id)
    initial = {'bb': comment.bb, 'author': comment.author}
    form = UserCommentForm(initial=initial)

    if request.method == 'POST':
        if request.user == comment.author:
            c_form = UserCommentForm(request.POST)

            if c_form.is_valid():
                c_form.save()

                messages.add_message(request, messages.SUCCESS,
                                        'Сообщение добавлено!')

                return redirect('main:index')
            else:
                form = c_form

                messages.add_message(request, messages.WARNING,
                                     'Сообщение не добавлено!')

    context = {'form': form, }

    return render(request, 'main/comment_add_answer.html', context)

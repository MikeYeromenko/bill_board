from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.core.paginator import Paginator
from django.core.signing import BadSignature
from django.db.models import Q, F
from django.http import Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import UpdateView, CreateView, TemplateView, DeleteView

from main.forms import ChangeUserInfoForm, RegisterUserForm, UserPasswordChangeForm, SearchForm, BbForm, AIFormSet, \
    UserCommentForm, GuestCommentForm
from main.models import AdvUser, SubRubric, Bb, Comment
from main.utilities import signer


def index(request):
    bbs = Bb.objects.all()[:10]
    form = SearchForm()
    return render(request, 'main/index.html', {'bbs': bbs, 'form': form})


def other_page(request, page):
    try:
        template = get_template(f'main/{page}.html')
    except TemplateDoesNotExist:
        return Http404
    return HttpResponse(template.render(request=request))


@login_required
def profile(request):
    bbs = Bb.objects.filter(author=request.user)
    return render(request, 'main/profile.html', {'bbs': bbs})


class BbLoginView(LoginView):
    template_name = 'main/login.html'


class BbLogoutView(LoginRequiredMixin, LogoutView):
    template_name = 'main/logout.html'


class ChangeUserInfoView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AdvUser
    form_class = ChangeUserInfoForm
    template_name = 'main/change_user_info.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Личные данные пользователя изменены'

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return UpdateView.dispatch(self, request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(queryset, pk=self.user_id)


class BbPasswordChangeView(PasswordChangeView):
    template_name = 'main/password_change_form.html'
    success_url = reverse_lazy('main:profile')
    success_message = 'Пароль пользователя изменен'
    form_class = UserPasswordChangeForm


class RegisterUserView(CreateView):
    model = AdvUser
    form_class = RegisterUserForm
    template_name = 'main/register_user.html'
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
        user.is_activated = True
        user.is_active = True
        user.save()
    return render(request, template)


class DeleteUserView(DeleteView):
    model = AdvUser
    template_name = 'main/delete_user.html'
    success_url = reverse_lazy('main:index')

    def dispatch(self, request, *args, **kwargs):
        self.user_id = request.user.pk
        return DeleteView.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Пользователь удалён')
        return DeleteView.post(self, request, *args, **kwargs)

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        return get_object_or_404(AdvUser, pk=self.user_id)


def by_rubric(request, pk):
    rubric = get_object_or_404(SubRubric, pk=pk)
    bbs = Bb.objects.filter(is_active=True, rubric=pk)
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
    else: page_num = 1
    page = paginator.get_page(page_num)
    context = {
        'rubric': rubric, 'page': page, 'bbs': page.object_list, 'form': form
    }
    return render(request, 'main/by_rubric.html', context)


def detail(request, rubric_pk, pk, comment_pk=None):
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additional_images.all()
    initial = {'bb': bb}
    if request.user.is_authenticated:
        initial['author'] = request.user.pk
        initial['author_name'] = request.user.username
        form_class = UserCommentForm
    else:
        form_class = GuestCommentForm
    form = form_class(initial=initial)
    if request.method.lower() == 'post':
        c_form = form_class(request.POST)
        if c_form.is_valid():
            com = c_form.save(commit=False)
            if comment_pk:
                com.parent_comment = get_object_or_404(Comment, pk=comment_pk)
            com.save()
            messages.add_message(request, messages.SUCCESS, 'Комментарий добавлен')
            return redirect('main:detail', rubric_pk=rubric_pk, pk=pk)
        else:
            form = c_form
            messages.add_message(request, messages.WARNING, 'Комментарий не добавлен')
    comments = Comment.objects.filter(bb=pk, is_active=True)
    context = {'form': form, 'comments': comments, 'bb': bb, 'ais': ais}
    return render(request, 'main/detail.html', context)


# isn't used anywhere
def profile_bb_detail(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additional_images.all()
    context = {'bb': bb, 'ais': ais}
    return render(request, 'main/detail.html', context)


@login_required
def profile_bb_add(request):
    if request.method.lower() == 'post':
        form = BbForm(request.POST, request.FILES)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
            messages.add_message(request, messages.SUCCESS, 'Объявление добавлено')
            return redirect('main:profile')
    if 'form' not in locals():
        form = BbForm(initial={'author': request.user.pk})
    if 'formset' not in locals():
        formset = AIFormSet()
    context = {'form': form, 'formset': formset}
    return render(request, 'main/profile_bb_add.html', context)


class BbUpdateView(LoginRequiredMixin, UpdateView):
    form_class = BbForm
    template_name = 'main/profile_bb_update.html'

    def post(self, request, *args, **kwargs):
        bb = get_object_or_404(Bb, pk=kwargs.get('pk'))
        form = BbForm(request.POST, request.FILES, instance=bb)
        if form.is_valid():
            bb = form.save()
            formset = AIFormSet(request.POST, request.FILES, instance=bb)
            if formset.is_valid():
                formset.save()
                messages.add_message(request, messages.SUCCESS, 'Объявление исправлено')
                return redirect('main:profile')
        if 'formset' not in locals():
            formset = AIFormSet()
        return render(request, 'main/profile_bb_update.html', {'form': form, 'formset': formset})

    def get(self, request, *args, **kwargs):
        bb = get_object_or_404(Bb, pk=kwargs.get('pk'))
        form = BbForm(instance=bb)
        formset = AIFormSet(instance=bb)
        return render(request, 'main/profile_bb_update.html', {'form': form, 'formset': formset})


class BbDeleteView(DeleteView):
    model = Bb
    template_name = 'main/profile_bb_delete.html'
    success_url = reverse_lazy('main:profile')


def likes_dislikes(request, choice, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if choice == 'like':
        comment.likes = F('likes') + 1
    else:
        comment.dislikes = F('dislikes') + 1
    comment.save()
    return redirect('main:detail', rubric_pk=comment.bb.rubric_id, pk=comment.bb.pk)


def complain(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.complain = True
    comment.save()
    return redirect('main:detail', rubric_pk=comment.bb.rubric_id, pk=comment.bb.pk)

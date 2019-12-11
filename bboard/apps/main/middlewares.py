from .models import SubRubric
from django.conf import settings
from datetime import timedelta, date


def bboard_context_processor(request):
    context = {}
    context['rubrics'] = SubRubric.objects.all()
    context['keyword'] = ''
    context['all'] = ''

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']

        if keyword:
            context['keyword'] = '?keyword' + keyword
            context['all'] = context['keyword']

    if 'page' in request.GET:
        page = request.GET['page']

        if page != '1':
            if context['all']:
                context['all'] += '&page=' + page
            else:
                context['all'] = '?page=' + page

    return context


# class KeepLoggedInMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request, *args, **kwargs):
#         response = self.get_response(request)
#
#         if not request.user.is_authenticated or not 'keep_me_logged' in request.session:
#             return response
#         if request.session['keep_me_logged'] != date.today():
#             request.session.set_expiry(timedelta(days=365))
#             request.session['keep_me_logged'] = date.today()
#         return response



    # def process_template_response(self, request, response):
    #     if not request.user.is_authenticated() or not 'keep_me_logged' in request.session:
    #         return
    #     if request.session['keep_me_logged'] != date.today():
    #         request.session.set_expiry(timedelta(days=365))
    #         request.session['keep_me_logged'] = date.today()
    #     return

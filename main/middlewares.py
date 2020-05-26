from main.models import SubRubric


def bboard_context_processor(request):
    context = {'rubrics': SubRubric.objects.all()}
    context['keyword'] = ''
    context['all'] = ''
    # Here we add to the context url, from which the request was. This is needed for reference "Назад" to
    # work correctly in app. "previous_url" - url, from which the request was
    # "http_refere" - full path, with host, from where the request was
    if request.META.get('HTTP_REFERER', False):
        context['previous_url'] = (
            request.META.get('HTTP_REFERER').replace(f'{request._current_scheme_host}', ''))
        context['previous_full_path'] = request.META.get('HTTP_REFERER')
    else:
        context['previous_url'] = '/'
        context['previous_full_path'] = f"http://{request.META.get('HTTP_HOST')}/"
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            context['keyword'] = '?keyword=' + keyword
            context['all'] = context['keyword']
    if 'page' in request.GET:
        page = request.GET['page']
        if page != 1:
            if context['all']:
                context['all'] += '&page=' + page
            else:
                context['all'] = '?page=' + page
    return context

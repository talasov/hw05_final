from django.core.paginator import Paginator
from django.conf import settings


def get_page(post_list, request):
    ''' Создание пагинации страницы '''
    paginator = Paginator(post_list, settings.QUANTITY_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from cms.models import Book


def book_list(request):
    """書籍の一覧"""
    #return HttpResponse('書籍の一覧')
    books = Book.objects.all().order_by('id')

    return render(request,
                  'cms/book_list.html',     # 使用するテンプレート
                  {'books': books})         # テンプレートに渡すデータ

def book_edit(request, book_id=None):
    """書籍の編集"""
    return HttpResponse('書籍の編集')


def book_del(request, book_id):
    """書籍の削除"""
    return HttpResponse('書籍の削除')
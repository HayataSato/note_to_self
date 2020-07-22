import datetime
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django_datatables_view.base_datatable_view import BaseDatatableView

from .models import Book, Summary
from .forms import BookForm, SummaryForm
from .esa import QueryEsa


@login_required
def index(request):
    """ Bookモデルからのobj取得 """
    book = Book.objects.order_by('pri')
    # 取得したタスクの登録日を年月日のみに書き換える（時間を削除）
    for i in range(len(book)):
        book[i].rgst = f'{book[i].rgst.year}年{book[i].rgst.month}月{book[i].rgst.day}日'
        book[i].name = abbrevBookName(book[i].name)
    return render(request, 'book_manager/index.html', {
        'book': book,
    })


class ArchiveBookDT(BaseDatatableView):
    # モデルの指定
    model = Book
    # 表示するフィールドの指定
    columns = ['name', 'category', 'time', 'rgst', 'ops']

    # 検索方法の指定：部分一致
    def get_filter_method(self):
        return super().FILTER_ICONTAINS

    def get_initial_queryset(self):
        return Book.objects.filter(status=True)

    def render_column(self, row, column):

        if column == 'name':
            return f'<a href="summary/{ row.pk }" class="stretched-link text-decoration-none" >{abbrevBookName(row.name)}</a>'
        elif column == 'rgst':
            rgst_jst = row.rgst.astimezone(datetime.timezone(datetime.timedelta(hours=+9)))
            rgst_jst_str = f'{rgst_jst.year}年{rgst_jst.month}月{rgst_jst.day}日'
            return rgst_jst_str
        elif column == 'ops':
            restore_data_url = f'status/{ row.pk }/'
            modify_url = f'mod/{ row.pk }/'
            delete_url = f'del/{ row.pk }/'
            return f'<div class="d-flex flex-row justify-content-around align-items-center">' \
                   f'<button class="btn btn-outline-primary btn-sm restore_confirm" data-toggle="modal" data-target="#restoreModal" data-name="{ row.name }" data-url="{ restore_data_url }">restore</button>' \
                   f'<a href="{ modify_url }" class="btn btn-outline-info btn-sm">Mod</a>' \
                   f'<button class="btn btn-outline-danger btn-sm del_confirm" data-toggle="modal" data-target="#deleteModal" data-name="{ row.name }" data-url="{ delete_url }">Del</button>' \
                   f'</div>'
        else:
            return super(ArchiveBookDT, self).render_column(row, column)


def book_edit(request, book_id=None):
    if book_id:  # 修正時：book_id が指定されている
        book = get_object_or_404(Book, pk=book_id)
    else:  # 追加時：book_idが追加されていない
        book = Book()

    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)  # POST された request データからフォームを作成
        if form.is_valid():  # フォームのバリデーション
            book = form.save(commit=False)
            book.save()
            return redirect('book_manager:index')
    else:  # GET の時
        form = BookForm(instance=book)  # bookインスタンスからフォームを作成

    return render(request, 'book_manager/edit.html', dict(form=form, book_id=book_id))


def book_status(request, book_id):
    """ taskの完了 """
    book = get_object_or_404(Book, pk=book_id)
    if book.status:
        book.status = False
    else:
        book.status = True
        book.pri = 0

    book.save()
    return redirect('book_manager:index')


def book_del(request, book_id):
    """ bookの削除 """
    book = get_object_or_404(Book, pk=book_id)
    book.delete()
    return redirect('book_manager:index')


class SummaryList(generic.ListView):
    """ Summaryの一覧 """
    # ListViewを使用してページネーションを実装
    context_object_name = 'summaries'
    template_name = 'book_manager/summary_list.html'
    paginate_by = 10  # 1ページあたりの表示件数

    def get(self, request, *args, **kwargs):
        book = get_object_or_404(Book, pk=kwargs['book_id'])  # 親モデル=raskの取得
        summaries = book.summaries.all().order_by('-updt')   # 任意のbookに紐付いた子モデル=summaryの取得(更新日が若い順に並べる)
        self.object_list = summaries
        # get_context_dataにリストにしたいQuerySetオブジェクトを渡せばおｋ
        context = self.get_context_data(object_list=self.object_list, book=book)
        return self.render_to_response(context)


class SummaryEdit(generic.TemplateView):
    """summaryの編集"""
    # TemplateViewにおけるインスタンスの初期化(setupメソッドのオーバーライド)
    def setup(self, request, *args, **kwargs):
        super().setup(self, request, *args, **kwargs)
        self.book = get_object_or_404(Book, pk=kwargs["book_id"])  # Book(親モデル)を読み込み
        # Summary(子モデル)の生成または読み込み
        if "summary_id" not in kwargs:
            # 作成時：summary_id が指定されていない -> Summaryインスタンス生成
            self.summary = Summary()
            self.f_new = True   # esa用の新規投稿フラグ (True -> post)
        else:
            # 修正時：summary_id が指定されている -> Summaryインスタンス読み込み
            self.summary = get_object_or_404(Summary, pk=kwargs["summary_id"])
            self.f_new = False  # esa用の新規投稿フラグ (False -> patch)

    def get(self, request, *args, **kwargs):
        form = SummaryForm(instance=self.summary)  # 読み込んだSummaryインスタンスからフォームを作成
        return render(request,
                      'book_manager/summary_edit.html',
                      dict(form=form, book_id=self.book.id, summary_id=self.summary.id))

    # requestインスタンスからPOSTされたフォームの値を取得してDBとesaに反映
    def post(self, request, *args, **kwargs):
        form = SummaryForm(request.POST, instance=self.summary)  # フォームの値を取得
        # 入力にエラーがないかをバリデート
        if form.is_valid():
            # フォームの入力をインスタンスに反映 (setupの分岐で用意していたSummaryインスタンスに反映)
            self.summary = form.save(commit=False)
            self.summary.book = self.book  # 親モデルをセット
            # esaに反映
            req = QueryEsa()
            if self.f_new:  # 作成時：フラグTrue
                res = req.post(book=self.book, summary=self.summary)
                if type(res) is str:  # APIエラー有り -> メッセージ ｜ 無し -> インスタンスにesa_idをセット
                    messages.warning(request, res + "<br><a href='https://suehiro24.esa.io/'> esaに新規投稿を反映できませんでした．</a>")
                else:
                    self.summary.esa_id = res.json()["number"]
            else:  # 修正時：フラグFalse
                res = req.patch(book=self.book, summary=self.summary)
                if type(res) is str:
                    messages.warning(request, res + "<br><a href='https://suehiro24.esa.io/'> esaに更新を反映できませんでした．</a>")
            # DBに反映
            self.summary.save()
        try:
            return redirect('book_manager:summary_detail', summary_id=self.summary.id)
        except:
            return redirect('book_manager:summary_list', book_id=self.book.id)


def summary_detail(request, summary_id):
    summary = Summary.objects.get(id=summary_id)
    return render(request, 'book_manager/summary_detail.html', {
        'summary': summary,
    })


def summary_del(request, book_id, summary_id):
    """summaryの削除"""
    summary = get_object_or_404(Summary, pk=summary_id)
    # esaAPIから削除
    req = QueryEsa()
    res = req.delete(esa_id=summary.esa_id)
    if type(res) is str:
        messages.warning(request, res + "<br><a href='https://suehiro24.esa.io/'> esaでは正常に削除されませんでした．</a>")
    # DBから削除
    summary.delete()
    return redirect('book_manager:summary_list', book_id=book_id)


def abbrevBookName(name):
    n = 0
    break_index = -1
    for i in range(len(name)):
        n += 1 if re.match(r"^[\x20-\x7e]*$", name[i]) else 2
        if n >= 38:
            break_index = i if i % 2 != 0 else i+1
            break
    result = name
    if break_index != -1:
        result = name[0:break_index] + "..."
    return result


### 関数で定義した summary_edit のview(ハンドラ的なヤツ)
# def summary_edit(request, book_id, summary_id=None):
#     """summaryの編集"""
#     book = get_object_or_404(Book, pk=book_id)  # 親の書籍を読み込み
#     if summary_id is None:  # 作成時：summary_id が指定されていない
#         summary = Summary()
#         f_new = True
#     else:                   # 修正時：summary_id が指定されている
#         summary = get_object_or_404(Summary, pk=summary_id)
#         f_new = False  # esa用の新規投稿フラグ (post or patch)
#     # HTTPメソッドが POST のとき
#     if request.method == 'POST':
#         form = SummaryForm(request.POST, instance=summary)  # POST された request データからフォームを作成
#         # DBへ反映
#         if form.is_valid():  # フォームのバリデーション結果に応じて分岐 (フォームに入力された値にエラーがないかをバリデート)
#             summary = form.save(commit=False)
#             summary.book = book  # この感想の、親の書籍をセット
#             # esa API
#             req = QueryEsa()
#             if f_new:  # 作成時：フラグTrue
#                 res = req.post(book=book, summary=summary)
#                 summary.esa_id = res.json()["number"]  # DBのesaidをセット
#             else:      # 修正時：フラグFalse
#                 req.patch(book=book, summary=summary)
#             summary.save()  # 反映
#         try:
#             return redirect('book_manager:summary_detail', summary_id=summary_id)
#         except:
#             return redirect('book_manager:summary_list', book_id=book_id)
#     # HTTPメソッドが GET のとき
#     else:
#         form = SummaryForm(instance=summary)  # summary インスタンスからフォームを作成
#
#     return render(request,
#                   'book_manager/summary_edit.html',
#                   dict(form=form, book_id=book_id, summary_id=summary_id))

import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from django.views import generic
from django_datatables_view.base_datatable_view import BaseDatatableView

from .models import Task, Summary
from .forms import TaskForm, SummaryForm
from .esa import QueryEsa

@login_required
def index(request):
    """ Taskモデルからのobj取得 """
    task = Task.objects.order_by('pri')
    # 取得したタスクの登録日を年月日のみに書き換える（時間を削除）
    for i in range(len(task)):
        task[i].rgst = f'{task[i].rgst.year}年{task[i].rgst.month}月{task[i].rgst.day}日'
    return render(request, 'tasker/index.html', {
        'task': task,
    })


class ArchiveTaskDT(BaseDatatableView):
    # モデルの指定
    model = Task
    # 表示するフィールドの指定
    columns = ['name', 'category', 'time', 'rgst', 'ops']

    # 検索方法の指定：部分一致
    def get_filter_method(self):
        return super().FILTER_ICONTAINS

    def get_initial_queryset(self):
        return Task.objects.filter(status=True)

    def render_column(self, row, column):

        if column == 'name':
            return f'<a href="summary/{ row.pk }" class="stretched-link text-decoration-none" >{row.name}</a>'
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
            return super(ArchiveTaskDT, self).render_column(row, column)


def task_edit(request, task_id=None):
    if task_id:  # 修正時：task_id が指定されている
        task = get_object_or_404(Task, pk=task_id)
    else:  # 追加時：task_idが追加されていない
        task = Task()

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)  # POST された request データからフォームを作成
        if form.is_valid():  # フォームのバリデーション
            task = form.save(commit=False)
            task.save()
            return redirect('tasker:index')
    else:  # GET の時
        form = TaskForm(instance=task)  # taskインスタンスからフォームを作成

    return render(request, 'tasker/edit.html', dict(form=form, task_id=task_id))


def task_status(request, task_id):
    """ taskの完了 """
    task = get_object_or_404(Task, pk=task_id)
    if task.status:
        task.status = False
    else:
        task.status = True
        task.pri = 0

    task.save()
    return redirect('tasker:index')


def task_del(request, task_id):
    """ taskの削除 """
    task = get_object_or_404(Task, pk=task_id)
    task.delete()
    return redirect('tasker:index')


class SummaryList(ListView):
    """ Summaryの一覧 """
    context_object_name = 'summaries'
    template_name = 'tasker/summary_list.html'
    paginate_by = 10  # １ページは最大10件ずつでページングする

    def get(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs['task_id'])  # 親の書籍を読む
        summaries = task.summaries.all().order_by('-updt')   # 書籍の子供の、感想を読む
        self.object_list = summaries

        context = self.get_context_data(object_list=self.object_list, task=task)
        return self.render_to_response(context)


def summary_edit(request, task_id, summary_id=None):
    """summaryの編集"""
    task = get_object_or_404(Task, pk=task_id)  # 親の書籍を読み込み
    if summary_id is None:  # 作成時：summary_id が指定されていない
        summary = Summary()
        f_new = True
    else:                   # 修正時：summary_id が指定されている
        summary = get_object_or_404(Summary, pk=summary_id)
        f_new = False  # esa用の新規投稿フラグ (post or patch)
    # HTTPメソッドが POST のとき
    if request.method == 'POST':
        form = SummaryForm(request.POST, instance=summary)  # POST された request データからフォームを作成
        # DBへ反映
        if form.is_valid():  # フォームのバリデーション結果に応じて分岐 (フォームに入力された値にエラーがないかをバリデート)
            summary = form.save(commit=False)
            summary.task = task  # この感想の、親の書籍をセット
            # esa API
            req = QueryEsa()
            if f_new:  # 作成時：フラグTrue
                res = req.post(taskname=task.name, taskcategory=task.category, title=summary.title, summary=summary.summary)
                summary.esa_id = res.json()["number"]  # DBのesaidをセット
            else:      # 修正時：フラグFalse
                req.patch(id=summary.esa_id, taskname=task.name, taskcategory=task.category, title=summary.title, summary=summary.summary)
            summary.save()  # 反映
        try:
            return redirect('tasker:summary_detail', summary_id=summary_id)
        except:
            return redirect('tasker:summary_list', task_id=task_id)
    # HTTPメソッドが GET のとき
    else:
        form = SummaryForm(instance=summary)  # summary インスタンスからフォームを作成

    return render(request,
                  'tasker/summary_edit.html',
                  dict(form=form, task_id=task_id, summary_id=summary_id))


def summary_detail(request, summary_id):
    summary = Summary.objects.get(id=summary_id)
    return render(request, 'tasker/summary_detail.html', {
        'summary': summary,
    })


def summary_del(request, task_id, summary_id):
    """summaryの削除"""
    summary = get_object_or_404(Summary, pk=summary_id)
    # esaAPIから削除
    req = QueryEsa()
    req.delete(id=summary.esa_id)
    # DBから削除
    summary.delete()
    return redirect('tasker:summary_list', task_id=task_id)


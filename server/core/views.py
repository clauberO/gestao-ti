import csv
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import connection, transaction
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST
from .forms import AppointmentForm, ClientForm, CommentForm, EquipmentForm, ProgressForm, UnitForm, WorkItemForm
from .models import Appointment, AuditEvent, Client, Equipment, Unit, WorkItem

MODULES = {
    "chamados": (WorkItem, WorkItemForm, "Chamados", "ticket"),
    "atividades": (WorkItem, WorkItemForm, "Atividades", "task"),
    "clientes": (Client, ClientForm, "Clientes", None),
    "unidades": (Unit, UnitForm, "Unidades", None),
    "equipamentos": (Equipment, EquipmentForm, "Equipamentos", None),
    "agenda": (Appointment, AppointmentForm, "Agenda", None),
}

def module_config(module):
    if module not in MODULES: raise Http404
    return MODULES[module]

def records(user, module):
    model, _, _, kind = module_config(module)
    qs = model.objects.all()
    if kind:
        qs = qs.filter(kind=kind).select_related("client", "assignee", "created_by", "unit")
        if not user.manages: qs = qs.filter(Q(assignee=user) | Q(created_by=user))
    elif model is Appointment:
        qs = qs.select_related("assignee").order_by("start_at", "pk")
        if not user.manages: qs = qs.filter(assignee=user)
    elif model is Equipment:
        qs = qs.select_related("unit", "unit__client")
    elif model is Unit:
        qs = qs.select_related("client")
    return qs

def audit(user, action, obj, summary):
    AuditEvent.objects.create(actor=user, action=action, model=obj._meta.label_lower, object_id=obj.pk, summary=summary[:250])

@login_required
@require_GET
def dashboard(request):
    tickets, tasks = records(request.user, "chamados"), records(request.user, "atividades")
    cards = [("Chamados em aberto", tickets.exclude(status="done").count()), ("Atividades pendentes", tasks.exclude(status="done").count()), ("Equipamentos", Equipment.objects.count()), ("Clientes ativos", Client.objects.filter(active=True).count())]
    columns = [(label, tasks.filter(status=status)[:6]) for status, label in WorkItem.Status.choices]
    return render(request, "core/dashboard.html", {"title": "Visão geral", "active": "inicio", "cards": cards, "columns": columns, "tickets": tickets[:5]})

@login_required
@require_GET
def listing(request, module):
    model, _, label, kind = module_config(module)
    qs = records(request.user, module)
    q = request.GET.get("q", "").strip()[:200]
    status = request.GET.get("status", "")
    if q:
        field = "title" if model in (WorkItem, Appointment) else "name"
        qs = qs.filter(**{field + "__icontains": q})
    if kind and status in WorkItem.Status.values: qs = qs.filter(status=status)
    return render(request, "core/list.html", {"title": label, "active": module, "module": module, "page": Paginator(qs, 20).get_page(request.GET.get("page")), "q": q, "status": status, "statuses": WorkItem.Status.choices if kind else [], "kind": kind, "can_create": request.user.manages})

@login_required
def edit(request, module, pk=None):
    model, form_class, label, kind = module_config(module)
    if not request.user.manages: raise PermissionDenied
    if request.method not in ("GET", "POST"): return HttpResponse(status=405)
    with transaction.atomic():
        obj = get_object_or_404(records(request.user, module).select_for_update(of=("self",)), pk=pk) if pk else model()
        current_version = obj.version if kind else None
        form = form_class(request.POST or None, instance=obj)
        valid = request.method == "POST" and form.is_valid()
        if valid and kind and pk and form.cleaned_data["version"] != current_version:
            form.add_error(None, "Este registro foi alterado por outra pessoa. Reabra a página antes de salvar.")
            valid = False
        if valid:
            obj = form.save(commit=False)
            if kind:
                obj.kind = kind
                obj.version = current_version + 1 if pk else 1
                if not pk: obj.created_by = request.user
            obj.save()
            audit(request.user, "update" if pk else "create", obj, f"{label}: registro {'atualizado' if pk else 'criado'}")
            messages.success(request, "Registro salvo com sucesso.")
            return redirect("detail", module=module, pk=obj.pk)
    return render(request, "core/form.html", {"title": ("Editar · " if pk else "Novo · ") + label, "active": module, "form": form, "module": module})

@login_required
@require_GET
def detail(request, module, pk):
    _, _, label, kind = module_config(module)
    obj = get_object_or_404(records(request.user, module), pk=pk)
    fields = []
    for field in obj._meta.fields:
        if field.name in ("id", "kind", "version", "created_by"): continue
        value = getattr(obj, "get_"+field.name+"_display")() if field.choices else getattr(obj, field.name)
        fields.append((field.verbose_name, value))
    return render(request, "core/detail.html", {"title": str(obj), "active": module, "module": module, "obj": obj, "fields": fields, "kind": kind, "comment_form": CommentForm(), "progress_form": ProgressForm(instance=obj) if kind else None, "events": AuditEvent.objects.filter(model=obj._meta.label_lower, object_id=obj.pk).select_related("actor")[:30]})

@login_required
@require_POST
def progress(request, module, pk):
    if module not in ("chamados", "atividades"): raise Http404
    with transaction.atomic():
        obj = get_object_or_404(records(request.user, module).select_for_update(of=("self",)), pk=pk)
        current = obj.version
        form = ProgressForm(request.POST, instance=obj)
        if not form.is_valid():
            return HttpResponse("Status inválido.", status=400)
        if form.cleaned_data["version"] != current:
            return HttpResponse("Registro alterado por outra pessoa. Atualize a página.", status=409)
        obj.version = current + 1
        obj.save(update_fields=["status", "version", "updated_at"])
        audit(request.user, "status", obj, "Status: " + obj.get_status_display())
    messages.success(request, "Status atualizado.")
    return redirect("detail", module=module, pk=pk)

@login_required
@require_POST
def comment(request, module, pk):
    if module not in ("chamados", "atividades"): raise Http404
    obj = get_object_or_404(records(request.user, module), pk=pk)
    form = CommentForm(request.POST)
    if not form.is_valid(): return HttpResponse("Comentário vazio ou muito longo.", status=400)
    with transaction.atomic():
        entry = form.save(commit=False)
        entry.item, entry.author = obj, request.user
        entry.save()
        audit(request.user, "comment", obj, "Comentário adicionado")
    return redirect("detail", module=module, pk=pk)

@login_required
@require_GET
def reports(request):
    if not request.user.manages: raise PermissionDenied
    return render(request, "core/reports.html", {"title": "Relatórios", "active": "relatorios", "counts": [(label, WorkItem.objects.filter(kind="ticket", status=status).count()) for status, label in WorkItem.Status.choices]})

def csv_cell(value):
    text = str(value or "")
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@")) or text.startswith(("\t", "\r", "\n")) else text

@login_required
@require_GET
def export(request):
    if not request.user.manages: raise PermissionDenied
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="chamados.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["ID", "Título", "Cliente", "Responsável", "Status", "Prioridade"])
    for obj in records(request.user, "chamados").iterator():
        writer.writerow([csv_cell(v) for v in [obj.pk, obj.title, obj.client, obj.assignee, obj.get_status_display(), obj.get_priority_display()]])
    return response

@require_GET
def health(request):
    try:
        with connection.cursor() as cursor: cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})


@login_required
def team(request):
    from .models import User
    if not request.user.administrator: raise PermissionDenied
    return render(request, "core/team.html", {"title": "Equipe e permissões", "active": "equipe", "members": User.objects.order_by("username")})

@login_required
def team_edit(request, pk=None):
    from .forms import TeamCreateForm, TeamEditForm
    from .models import User
    if not request.user.administrator: raise PermissionDenied
    if request.method not in ("GET", "POST"): return HttpResponse(status=405)
    with transaction.atomic():
        obj = get_object_or_404(User.objects.select_for_update(), pk=pk) if pk else None
        if obj and obj.is_superuser and not request.user.is_superuser: raise PermissionDenied
        form = (TeamEditForm if pk else TeamCreateForm)(request.POST or None, instance=obj)
        valid = request.method == "POST" and form.is_valid()
        if valid and pk == request.user.pk and (not form.cleaned_data["is_active"] or form.cleaned_data["role"] != request.user.role):
            form.add_error(None, "Você não pode desativar sua própria conta ou alterar seu próprio perfil.")
            valid = False
        if valid:
            obj = form.save()
            audit(request.user, "team_update" if pk else "team_create", obj, "Conta da equipe atualizada" if pk else "Conta da equipe criada")
            messages.success(request, "Conta salva com sucesso.")
            return redirect("team")
    return render(request, "core/team_form.html", {"title": "Editar conta" if pk else "Nova conta", "active": "equipe", "form": form})

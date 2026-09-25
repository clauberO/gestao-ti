from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        MANAGER = "manager", "Gestor"
        TECHNICIAN = "technician", "Técnico"
    role = models.CharField("perfil", max_length=20, choices=Role.choices, default=Role.TECHNICIAN)
    @property
    def manages(self):
        return self.is_superuser or self.role in (self.Role.ADMIN, self.Role.MANAGER)
    @property
    def administrator(self):
        return self.is_superuser or self.role == self.Role.ADMIN
    def __str__(self):
        return self.get_full_name() or self.username

class Timestamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
        ordering = ["-created_at", "-pk"]

class Client(Timestamped):
    name = models.CharField("nome", max_length=160)
    email = models.EmailField("e-mail", blank=True)
    phone = models.CharField("telefone", max_length=30, blank=True)
    active = models.BooleanField("ativo", default=True)
    notes = models.TextField("observações", blank=True, max_length=5000)
    def __str__(self): return self.name

class Unit(Timestamped):
    name = models.CharField("nome", max_length=160)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="cliente")
    address = models.CharField("endereço", max_length=250, blank=True)
    active = models.BooleanField("ativa", default=True)
    def __str__(self): return f"{self.name} · {self.client}"

class Equipment(Timestamped):
    class Status(models.TextChoices):
        IN_USE = "in_use", "Em uso"
        MAINTENANCE = "maintenance", "Em manutenção"
        INACTIVE = "inactive", "Inativo"
    name = models.CharField("nome", max_length=160)
    asset_tag = models.CharField("patrimônio", max_length=60, unique=True)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name="unidade")
    model = models.CharField("modelo", max_length=160, blank=True)
    serial = models.CharField("número de série", max_length=120, blank=True)
    status = models.CharField("situação", max_length=20, choices=Status.choices, default=Status.IN_USE)
    notes = models.TextField("observações", max_length=5000, blank=True)
    def __str__(self): return f"{self.asset_tag} · {self.name}"

class WorkItem(Timestamped):
    class Kind(models.TextChoices):
        TICKET = "ticket", "Chamado"
        TASK = "task", "Atividade"
    class Status(models.TextChoices):
        OPEN = "open", "Aberto"
        IN_PROGRESS = "in_progress", "Em andamento"
        WAITING = "waiting", "Aguardando"
        DONE = "done", "Concluído"
    class Priority(models.TextChoices):
        LOW = "low", "Baixa"
        MEDIUM = "medium", "Média"
        HIGH = "high", "Alta"
        CRITICAL = "critical", "Crítica"
    kind = models.CharField(max_length=10, choices=Kind.choices)
    title = models.CharField("título", max_length=180)
    description = models.TextField("descrição", max_length=10000)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="cliente", null=True, blank=True)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, verbose_name="unidade", null=True, blank=True)
    assignee = models.ForeignKey(User, on_delete=models.PROTECT, related_name="assigned_items", verbose_name="responsável", null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_items")
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.OPEN)
    priority = models.CharField("prioridade", max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    due_at = models.DateTimeField("prazo", null=True, blank=True)
    version = models.PositiveIntegerField(default=1)
    class Meta(Timestamped.Meta):
        indexes = [models.Index(fields=["kind", "status"]), models.Index(fields=["assignee", "status"])]
    def clean(self):
        if self.unit_id and self.unit.client_id != self.client_id:
            raise ValidationError({"unit": "A unidade deve pertencer ao cliente selecionado."})
    def __str__(self): return f"#{self.pk} · {self.title}"

class Appointment(Timestamped):
    title = models.CharField("título", max_length=180)
    assignee = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="responsável")
    start_at = models.DateTimeField("início")
    end_at = models.DateTimeField("fim")
    location = models.CharField("local", max_length=250, blank=True)
    notes = models.TextField("observações", max_length=5000, blank=True)
    def clean(self):
        if self.start_at and self.end_at and self.end_at <= self.start_at:
            raise ValidationError({"end_at": "O fim deve ser posterior ao início."})
    def __str__(self): return self.title

class Comment(models.Model):
    item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    body = models.TextField("comentário", max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["created_at", "pk"]

class AuditEvent(models.Model):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=30)
    model = models.CharField(max_length=60)
    object_id = models.PositiveBigIntegerField()
    summary = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created_at", "-pk"]

class LoginBucket(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    started_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)

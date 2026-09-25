from django import forms
from .models import Appointment, Client, Comment, Equipment, Unit, User, WorkItem

class WorkItemForm(forms.ModelForm):
    version = forms.IntegerField(widget=forms.HiddenInput, required=False)
    class Meta:
        model = WorkItem
        fields = ["title", "description", "client", "unit", "assignee", "status", "priority", "due_at", "version"]
        widgets = {"due_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"), "description": forms.Textarea(attrs={"rows": 5})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignee"].queryset = User.objects.filter(is_active=True)

class ProgressForm(forms.ModelForm):
    version = forms.IntegerField(widget=forms.HiddenInput)
    class Meta:
        model = WorkItem
        fields = ["status", "version"]

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 3})}

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "email", "phone", "active", "notes"]

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ["name", "client", "address", "active"]

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ["name", "asset_tag", "unit", "model", "serial", "status", "notes"]

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["title", "assignee", "start_at", "end_at", "location", "notes"]
        widgets = {field: forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M") for field in ("start_at", "end_at")}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignee"].queryset = User.objects.filter(is_active=True)

from django.contrib.auth.forms import UserCreationForm

class TeamCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email", "role"]

class TeamEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "role", "is_active"]

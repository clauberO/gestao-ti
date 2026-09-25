from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import Client as Browser, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from .models import Appointment, AuditEvent, Client, Equipment, Unit, WorkItem

User = get_user_model()

@override_settings(STORAGES={"default": {"BACKEND": "django.core.files.storage.FileSystemStorage"}, "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}})
class ApplicationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user("gestor", password="manager-test-only!938", role="manager")
        cls.tech = User.objects.create_user("tecnico", password="tech-test-only!938")
        cls.other = User.objects.create_user("outro", password="other-test-only!938")
        cls.admin = User.objects.create_superuser("admin", "admin@example.test", "admin-test-only!938", role="admin")
        cls.customer = Client.objects.create(name="Cliente A")
        cls.unit = Unit.objects.create(name="Matriz", client=cls.customer)
        cls.item = WorkItem.objects.create(kind="ticket", title="Impressora", description="Sem comunicação", client=cls.customer, unit=cls.unit, assignee=cls.tech, created_by=cls.manager)
        cls.hidden = WorkItem.objects.create(kind="ticket", title="Restrito outro técnico", description="Interno", assignee=cls.other, created_by=cls.manager)
        cls.equipment = Equipment.objects.create(name="Roteador", asset_tag="PAT-001", unit=cls.unit)
        cls.appointment = Appointment.objects.create(title="Visita", assignee=cls.tech, start_at=timezone.now(), end_at=timezone.now()+timedelta(hours=1))

    def test_anonymous_redirected_and_no_record_leak(self):
        response = self.client.get(reverse("detail", args=["chamados", self.item.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_real_login_and_invalid_password(self):
        response = self.client.post(reverse("login"), {"username": "tecnico", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        response = self.client.post(reverse("login"), {"username": "tecnico", "password": "tech-test-only!938"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)
        self.assertNotEqual(self.tech.password, "tech-test-only!938")

    def test_manager_pages_and_forms_render(self):
        self.client.force_login(self.manager)
        for url in [reverse("dashboard"), reverse("reports"), reverse("password_change")]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        for module in ["chamados", "atividades", "clientes", "unidades", "equipamentos", "agenda"]:
            for route in ["list", "create"]:
                with self.subTest(module=module, route=route):
                    self.assertEqual(self.client.get(reverse(route, args=[module])).status_code, 200)
        for module, pk in [("chamados", self.item.pk), ("clientes", self.customer.pk), ("unidades", self.unit.pk), ("equipamentos", self.equipment.pk), ("agenda", self.appointment.pk)]:
            self.assertEqual(self.client.get(reverse("detail", args=[module, pk])).status_code, 200)

    def test_technician_cannot_access_other_work_or_change_master_data(self):
        self.client.force_login(self.tech)
        url = reverse("detail", args=["chamados", self.hidden.pk])
        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(self.client.post(reverse("progress", args=["chamados", self.hidden.pk]), {"status": "done", "version": 1}).status_code, 404)
        response = self.client.get(reverse("list", args=["chamados"]))
        self.assertNotContains(response, "Restrito outro técnico")
        for route, args in [("create", ["clientes"]), ("edit", ["chamados", self.item.pk]), ("reports", []), ("export", []), ("team", [])]:
            self.assertEqual(self.client.get(reverse(route, args=args)).status_code, 403)

    def test_manager_creates_persistent_ticket_with_audit(self):
        self.client.force_login(self.manager)
        response = self.client.post(reverse("create", args=["chamados"]), {"title": "Novo chamado", "description": "Teste", "client": self.customer.pk, "unit": self.unit.pk, "assignee": self.tech.pk, "status": "open", "priority": "high"})
        self.assertEqual(response.status_code, 302)
        item = WorkItem.objects.get(title="Novo chamado")
        self.assertEqual(item.created_by, self.manager)
        self.assertEqual(item.version, 1)
        self.assertTrue(AuditEvent.objects.filter(object_id=item.pk, action="create", actor=self.manager).exists())
        independent = Browser()
        independent.force_login(self.tech)
        self.assertContains(independent.get(response.url), "Novo chamado")

    def test_mismatched_unit_rejected(self):
        other_client = Client.objects.create(name="Outro cliente")
        self.client.force_login(self.manager)
        response = self.client.post(reverse("create", args=["chamados"]), {"title": "Inválido", "description": "Teste", "client": other_client.pk, "unit": self.unit.pk, "status": "open", "priority": "high"})
        self.assertContains(response, "A unidade deve pertencer")
        self.assertFalse(WorkItem.objects.filter(title="Inválido").exists())

    def test_progress_cannot_reassign_and_conflicts_are_detected(self):
        self.client.force_login(self.tech)
        url = reverse("progress", args=["chamados", self.item.pk])
        response = self.client.post(url, {"status": "done", "version": 1, "assignee": self.other.pk})
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, "done")
        self.assertEqual(self.item.assignee, self.tech)
        self.assertEqual(self.item.version, 2)
        self.assertEqual(self.client.post(url, {"status": "open", "version": 1}).status_code, 409)
        self.item.refresh_from_db()
        self.assertEqual(self.item.status, "done")

    def test_manager_edit_conflict_preserves_new_data(self):
        self.client.force_login(self.manager)
        WorkItem.objects.filter(pk=self.item.pk).update(version=2, title="Título atualizado")
        response = self.client.post(reverse("edit", args=["chamados", self.item.pk]), {"title": "Velho", "description": "Teste", "status": "open", "priority": "low", "version": 1})
        self.assertContains(response, "alterado por outra pessoa")
        self.item.refresh_from_db()
        self.assertEqual(self.item.title, "Título atualizado")

    def test_comment_escaped_and_author_from_session(self):
        self.client.force_login(self.tech)
        response = self.client.post(reverse("comment", args=["chamados", self.item.pk]), {"body": "<script>alert(1)</script>", "author": self.admin.pk})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.item.comments.get().author, self.tech)
        response = self.client.get(response.url)
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_csrf_required_and_logout_post_only(self):
        secure_browser = Browser(enforce_csrf_checks=True)
        secure_browser.force_login(self.manager)
        self.assertEqual(secure_browser.post(reverse("create", args=["clientes"]), {"name": "X"}).status_code, 403)
        self.client.force_login(self.tech)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertEqual(self.client.post(reverse("logout")).status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_throttled_on_both_forms(self):
        for _ in range(10):
            self.client.post(reverse("login"), {"username": "ghost", "password": "invalid"})
        self.assertEqual(self.client.post("/admin/login/", {"username": "ghost", "password": "invalid"}).status_code, 429)

    def test_csv_neutralizes_formulas(self):
        WorkItem.objects.filter(pk=self.item.pk).update(title="  =HYPERLINK(1)")
        self.client.force_login(self.manager)
        response = self.client.get(reverse("export"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("'  =HYPERLINK(1)", response.content.decode())

    def test_admin_creates_user_and_rejects_weak_password(self):
        self.client.force_login(self.admin)
        payload = {"username": "novo", "role": "technician", "password1": "123", "password2": "123"}
        self.assertEqual(self.client.post(reverse("team_create"), payload).status_code, 200)
        self.assertFalse(User.objects.filter(username="novo").exists())
        payload.update(password1="new-account-test!3217", password2="new-account-test!3217")
        self.assertEqual(self.client.post(reverse("team_create"), payload).status_code, 302)
        member = User.objects.get(username="novo")
        self.assertTrue(member.check_password(payload["password1"]))
        self.assertFalse(member.is_superuser)
        self.assertFalse(member.is_staff)

    def test_admin_cannot_disable_self(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("team_edit", args=[self.admin.pk]), {"role": "admin", "is_active": ""})
        self.assertContains(response, "Você não pode desativar")
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_inactive_account_denied(self):
        self.tech.is_active = False
        self.tech.save()
        self.assertFalse(self.client.login(username="tecnico", password="tech-test-only!938"))

    def test_headers_and_health(self):
        self.client.force_login(self.tech)
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertIn("frame-ancestors 'none'", response["Content-Security-Policy"])
        self.assertEqual(self.client.get(reverse("health")).json(), {"status": "ok"})

    def test_invalid_appointment_times(self):
        self.client.force_login(self.manager)
        response = self.client.post(reverse("create", args=["agenda"]), {"title": "Visita inválida", "assignee": self.tech.pk, "start_at": "2026-10-01T15:00", "end_at": "2026-10-01T14:00"})
        self.assertContains(response, "O fim deve ser posterior")
        self.assertFalse(Appointment.objects.filter(title="Visita inválida").exists())

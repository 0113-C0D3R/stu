# students/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    # شغّل عند ترحيل تطبيق students فقط
    if sender.name != "students":
        return

    # الموديلات المُدارة
    model_names = [
        "Student", "Document", "Correspondent",
        "ExecutiveDirector", "GeneratedLetter",
        "ReferenceCounter", "SiteSettings",
    ]

    def perm_codes(actions, models):
        codes = []
        for m in models:
            mn = m.lower()
            for a in actions:
                codes.append(f"{a}_{mn}")
        return codes

    groups_spec = {
        "مسؤول النظام": {
            "perms": perm_codes(["view", "add", "change", "delete"], model_names),
        },
        "محرر": {
            "perms": (
                perm_codes(["view", "add", "change"], ["Student","Document","Correspondent","GeneratedLetter"])
                + perm_codes(["view"], ["ExecutiveDirector","ReferenceCounter","SiteSettings"])
            ),
        },
        "متصفح": {
            "perms": perm_codes(["view"], model_names),
        },
    }

    for group_name, spec in groups_spec.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        perms = Permission.objects.filter(codename__in=spec["perms"])
        group.permissions.set(perms)  # idempotent
        group.save()

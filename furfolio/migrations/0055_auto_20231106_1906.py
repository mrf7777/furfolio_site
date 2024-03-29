# Generated by Django 4.2.4 on 2023-11-06 19:06

from django.db import migrations


def add_tag_moderators_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    tag_permissions = Permission.objects.filter(
        codename__in=[
            "add_tag",
            "change_tag",
            "delete_tag",
            "view_tag",
        ]
    )

    tag_mod_group = Group(name="tag_mods")
    tag_mod_group.save()
    tag_mod_group.permissions.set(tag_permissions)
    tag_mod_group.save()


class Migration(migrations.Migration):
    dependencies = [
        ("furfolio", "0054_tagcategory_tag"),
    ]

    operations = [
        migrations.RunPython(add_tag_moderators_group),
    ]

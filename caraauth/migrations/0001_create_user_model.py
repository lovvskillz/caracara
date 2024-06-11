import datetime

import django.contrib.auth.models
import django.core.validators
import django.utils.timezone
from django.db import migrations, models

import caraauth.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text=(
                            "Designates that this user has all permissions without"
                            " explicitly assigning them."
                        ),
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text=(
                            "Designates whether the user can log into this admin site."
                        ),
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text=(
                            "Designates whether this user should be treated as active."
                            " Unselect this instead of deleting accounts."
                        ),
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        blank=True,
                        default=django.utils.timezone.now,
                        verbose_name="Created at",
                    ),
                ),
                (
                    "modified_at",
                    models.DateTimeField(
                        blank=True,
                        default=datetime.datetime(
                            1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
                        ),
                        verbose_name="Modified at",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text=(
                            "Required. 5 - 64 characters. Letters, digits and _ only."
                        ),
                        max_length=64,
                        unique=True,
                        validators=[
                            django.core.validators.MinLengthValidator(limit_value=5),
                            caraauth.validators.UsernameValidator(),
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="email address"
                    ),
                ),
                (
                    "password",
                    models.CharField(
                        help_text=(
                            "Required. Need to have at least 8 characters containing"
                            " letters and digits."
                        ),
                        max_length=128,
                        validators=[caraauth.validators.PasswordValidator()],
                        verbose_name="password",
                    ),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="Last Login"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text=(
                            "The groups this user belongs to. A user will get all"
                            " permissions granted to each of their groups."
                        ),
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
    ]

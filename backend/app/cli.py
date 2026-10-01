import click

from app.services import ticket_service
from app.services import user_service


def register_cli(app):
    @app.cli.command("escalate-sla")
    def escalate_sla():
        overdue_count, approaching_count = ticket_service.escalate_overdue_tickets()
        click.echo(
            f"Прострочено: {overdue_count}, наближається до дедлайну: {approaching_count}"
        )

    @app.cli.command("create-admin")
    @click.argument("email")
    @click.option("--name", default="Адміністратор")
    @click.password_option()
    def create_admin(email, name, password):
        user = user_service.create_admin(email, password, name)
        click.echo(f"Створено admin: {user.email}")

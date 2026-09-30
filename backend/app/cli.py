import click

from app.services import ticket_service


def register_cli(app):
    @app.cli.command("escalate-sla")
    def escalate_sla():
        overdue_count, approaching_count = ticket_service.escalate_overdue_tickets()
        click.echo(
            f"Прострочено: {overdue_count}, наближається до дедлайну: {approaching_count}"
        )

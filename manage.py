from app import create_app, db
from app.models.demanda_tipo import DemandaTipo
from app.models.resumo_familia_ia import ResumoFamiliaIA
from app.models.password_reset_token import PasswordResetToken
from seeds.admin_user_seed import seed_admin_user
from seeds.familias_seed import seed_familias
from app.models.usuario import Usuario
import click

app = create_app()

def seed_demanda_tipo():
    if not DemandaTipo.query.first():
        tipos = [
            (1, "Cursos profissionalizantes"),
            (2, "Equipamentos para casa"),
            (3, "Serviços domésticos"),
            (4, "Medicamentos"),
            (5, "Vaga em escola"),
            (6, "Necessidades jurídicas"),
            (7, "Outros"),
        ]
        for id_, nome in tipos:
            db.session.add(DemandaTipo(demanda_tipo_id=id_, demanda_tipo_nome=nome))
        db.session.commit()


@click.command()
@click.option('--admin-password', hide_input=True,
              envvar='SENHA_ADMIN', help='Password for the initial admin user.')
@click.option('--with-demo-data', is_flag=True, help='Inclui as quatro famílias fictícias para testes.')
def initialize(admin_password, with_demo_data):
    """Create local SQLite databases and seed lookup data and the admin account."""
    with app.app_context():
        from sqlalchemy import inspect
        admin_existe = inspect(db.engine).has_table('usuarios') and Usuario.query.filter_by(login='admin').first() is not None
        if not admin_existe:
            if not admin_password:
                admin_password = click.prompt('Senha inicial do administrador', hide_input=True, confirmation_prompt=True)
            if not admin_password.strip():
                raise click.ClickException('A senha do administrador não pode ser vazia.')
            if app.config['ENV'] == 'production' and (
                len(admin_password) < 12 or admin_password.startswith('SUBSTITUA')
                or admin_password in {'FormiguinhasLocal123!', 'choose-your-own-password'}
            ):
                raise click.ClickException('Defina uma senha de produção própria com pelo menos 12 caracteres.')
        db.create_all()
        engine = app.extensions['pre_cadastro_engine']
        try:
            # Pre-registration uses the same family/contact schema in a separate file.
            db.metadata.create_all(engine)
        finally:
            engine.dispose()
        seed_demanda_tipo()
        seed_admin_user(admin_password)
        familias_criadas = seed_familias() if with_demo_data else 0
    click.echo(f'Famílias fictícias criadas: {familias_criadas}.')
    click.echo('Databases initialized. Log in as admin with your chosen password.')


if __name__ == "__main__":
    initialize()


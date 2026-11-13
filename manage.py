from app import create_app, db
from app.models.demanda_tipo import DemandaTipo
from app.models.resumo_familia_ia import ResumoFamiliaIA
from app.models.password_reset_token import PasswordResetToken
from seeds.admin_user_seed import seed_admin_user
from seeds.familias_seed import seed_familias
from sqlalchemy import create_engine
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
@click.option('--admin-password', prompt=True, hide_input=True, confirmation_prompt=True,
              envvar='SENHA_ADMIN', help='Password for the initial admin user.')
def initialize(admin_password):
    """Create local SQLite databases and seed lookup data and the admin account."""
    import os
    os.environ['SENHA_ADMIN'] = admin_password
    with app.app_context():
        db.create_all()
        engine = create_engine(app.config['SQLALCHEMY_PRE_CADASTRO_URI'])
        try:
            # Pre-registration uses the same family/contact schema in a separate file.
            db.metadata.create_all(engine)
        finally:
            engine.dispose()
        seed_demanda_tipo()
        seed_admin_user()
        familias_criadas = seed_familias()
    click.echo(f'Famílias fictícias criadas: {familias_criadas}.')
    click.echo('Databases initialized. Log in as admin with your chosen password.')


if __name__ == "__main__":
    initialize()


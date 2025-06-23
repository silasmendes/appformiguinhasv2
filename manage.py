from app import create_app, db
from app.models.demanda_tipo import DemandaTipo

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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_demanda_tipo()


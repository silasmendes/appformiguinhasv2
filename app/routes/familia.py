from flask import Blueprint, request, jsonify, session
from marshmallow import ValidationError
from app.models.familia import Familia
from app.models.atendimento import Atendimento
from app.schemas.familia import FamiliaSchema
from app import db
from sqlalchemy import func, or_

bp = Blueprint("familias", __name__, url_prefix="/familias")

familia_schema = FamiliaSchema()
familias_schema = FamiliaSchema(many=True)

@bp.route("", methods=["POST"])
def criar_familia():
    data = request.get_json()
    try:
        nova_familia = familia_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    db.session.add(nova_familia)
    db.session.commit()
    return familia_schema.jsonify(nova_familia), 201

@bp.route("", methods=["GET"])
def listar_familias():
    familias = Familia.query.all()
    return familias_schema.jsonify(familias), 200


@bp.route("/busca", methods=["GET"])
def buscar_familias():
    termo = request.args.get("q", "")
    query = Familia.query
    # Busca tanto por CPF quanto por nome (similar à query T-SQL fornecida)
    query = query.filter(
        or_(
            Familia.cpf.ilike(f"%{termo}%"),
            Familia.nome_responsavel.ilike(f"%{termo}%")
        )
    )
    familias = query.all()

    resultados = []
    for familia in familias:
        ultimo = db.session.query(func.max(Atendimento.data_hora_atendimento)).filter_by(familia_id=familia.familia_id).scalar()
        resultados.append({
            "familia_id": familia.familia_id,
            "nome_responsavel": familia.nome_responsavel,
            "data_nascimento": familia.data_nascimento.isoformat() if familia.data_nascimento else None,
            "cpf": familia.cpf,
            "ultimo_atendimento": ultimo.date().isoformat() if ultimo else None,
        })
    return jsonify(resultados)

@bp.route("/<int:familia_id>", methods=["GET"])
def obter_familia(familia_id):
    familia = db.session.get(Familia, familia_id)
    if not familia:
        return jsonify({"mensagem": "Família não encontrada"}), 404
    return familia_schema.jsonify(familia)

@bp.route("/<int:familia_id>", methods=["PUT"])
def atualizar_familia(familia_id):
    familia = db.session.get(Familia, familia_id)
    if not familia:
        return jsonify({"mensagem": "Família não encontrada"}), 404

    data = request.get_json()
    familia = familia_schema.load(data, instance=familia, partial=True)

    db.session.commit()
    return familia_schema.jsonify(familia)


@bp.route("/upsert/familia/<int:familia_id>", methods=["PUT"])
def upsert_familia_por_familia(familia_id):
    """Rota de upsert (criação ou atualização baseada em familia_id).

    Quando ``familia_id`` é ``0`` consideramos uma criação de família e
    deixamos o banco gerar a chave primária.
    """

    data = request.get_json() or {}
    data.pop("familia_id", None)

    session_familia_id = session.get("familia_id")

    if familia_id == 0 and session_familia_id:
        familia_id = session_familia_id

    try:
        if familia_id == 0:
            familia = familia_schema.load(data)
            db.session.add(familia)
            db.session.commit()
            session["familia_id"] = familia.familia_id
            return familia_schema.jsonify(familia), 201

        existente = db.session.get(Familia, familia_id)
        if existente:
            familia = familia_schema.load(data, instance=existente, partial=True)
        else:
            data["familia_id"] = familia_id
            familia = familia_schema.load(data)
            db.session.add(familia)

        db.session.commit()
        session["familia_id"] = familia.familia_id
        return familia_schema.jsonify(familia)
    except ValidationError as err:
        db.session.rollback()
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"mensagem": f"Erro interno: {str(e)}"}), 500

@bp.route("/<int:familia_id>", methods=["DELETE"])
def deletar_familia(familia_id):
    familia = db.session.get(Familia, familia_id)
    if not familia:
        return jsonify({"mensagem": "Família não encontrada"}), 404

    db.session.delete(familia)
    db.session.commit()
    return jsonify({"mensagem": "Família deletada com sucesso"}), 200

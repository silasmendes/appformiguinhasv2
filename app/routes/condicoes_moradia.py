from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.models.condicoes_moradia import CondicaoMoradia
from app.schemas.condicoes_moradia import CondicaoMoradiaSchema
from app import db

bp = Blueprint("condicoes_moradia", __name__, url_prefix="/condicoes_moradia")

condicao_schema = CondicaoMoradiaSchema()
condicoes_schema = CondicaoMoradiaSchema(many=True)


@bp.route("", methods=["POST"])
@jwt_required()
def criar_condicao_moradia():
    data = request.get_json()
    try:
        nova_condicao = condicao_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(nova_condicao)
    db.session.commit()
    return condicao_schema.jsonify(nova_condicao), 201


@bp.route("", methods=["GET"])
@jwt_required()
def listar_condicoes_moradia():
    condicoes = CondicaoMoradia.query.all()
    return condicoes_schema.jsonify(condicoes), 200


@bp.route("/<int:moradia_id>", methods=["GET"])
@jwt_required()
def obter_condicao_moradia(moradia_id):
    condicao = db.session.get(CondicaoMoradia, moradia_id)
    if not condicao:
        return jsonify({"mensagem": "Condição de moradia não encontrada"}), 404
    return condicao_schema.jsonify(condicao)


@bp.route("/<int:moradia_id>", methods=["PUT"])
@jwt_required()
def atualizar_condicao_moradia(moradia_id):
    condicao = db.session.get(CondicaoMoradia, moradia_id)
    if not condicao:
        return jsonify({"mensagem": "Condição de moradia não encontrada"}), 404

    data = request.get_json()
    condicao = condicao_schema.load(data, instance=condicao, partial=True)

    db.session.commit()
    return condicao_schema.jsonify(condicao)


@bp.route("/<int:moradia_id>", methods=["DELETE"])
@jwt_required()
def deletar_condicao_moradia(moradia_id):
    condicao = db.session.get(CondicaoMoradia, moradia_id)
    if not condicao:
        return jsonify({"mensagem": "Condição de moradia não encontrada"}), 404

    db.session.delete(condicao)
    db.session.commit()
    return jsonify({"mensagem": "Condição de moradia deletada com sucesso"}), 200


@bp.route("/upsert/familia/<int:familia_id>", methods=["PUT"])
@jwt_required()
def upsert_condicao_moradia_por_familia(familia_id):
    """Rota de upsert (criação ou atualização baseada em familia_id)."""
    data = request.get_json() or {}

    # converte strings vazias em None para evitar erros de validação em campos
    # numéricos opcionais
    num_fields = [
        "valor_aluguel",
        "quantidade_camas",
        "quantidade_tvs",
        "quantidade_ventiladores",
    ]
    for field in num_fields:
        if field in data and data[field] == "":
            data[field] = None

    existente = CondicaoMoradia.query.filter_by(familia_id=familia_id).first()

    try:
        if existente:
            condicao = condicao_schema.load(data, instance=existente, partial=True)
        else:
            data["familia_id"] = familia_id
            condicao = condicao_schema.load(data)
            db.session.add(condicao)
        db.session.commit()
    except ValidationError as err:
        db.session.rollback()
        return jsonify(err.messages), 400

    return condicao_schema.jsonify(condicao)

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models.composicao_familiar import ComposicaoFamiliar
from app.schemas.composicao_familiar import ComposicaoFamiliarSchema
from app import db

bp = Blueprint("composicao_familiar", __name__, url_prefix="/composicao_familiar")

composicao_schema = ComposicaoFamiliarSchema()
composicoes_schema = ComposicaoFamiliarSchema(many=True)


@bp.route("", methods=["POST"])
def criar_composicao():
    data = request.get_json()
    try:
        nova_composicao = composicao_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(nova_composicao)
    db.session.commit()
    return composicao_schema.jsonify(nova_composicao), 201


@bp.route("", methods=["GET"])
def listar_composicoes():
    composicoes = ComposicaoFamiliar.query.all()
    return composicoes_schema.jsonify(composicoes), 200


@bp.route("/<int:composicao_id>", methods=["GET"])
def obter_composicao(composicao_id):
    composicao = db.session.get(ComposicaoFamiliar, composicao_id)
    if not composicao:
        return jsonify({"mensagem": "Composicao familiar não encontrada"}), 404
    return composicao_schema.jsonify(composicao)


@bp.route("/<int:composicao_id>", methods=["PUT"])
def atualizar_composicao(composicao_id):
    composicao = db.session.get(ComposicaoFamiliar, composicao_id)
    if not composicao:
        return jsonify({"mensagem": "Composicao familiar não encontrada"}), 404

    data = request.get_json()
    composicao = composicao_schema.load(data, instance=composicao, partial=True)

    db.session.commit()
    return composicao_schema.jsonify(composicao)


@bp.route("/<int:composicao_id>", methods=["DELETE"])
def deletar_composicao(composicao_id):
    composicao = db.session.get(ComposicaoFamiliar, composicao_id)
    if not composicao:
        return jsonify({"mensagem": "Composicao familiar não encontrada"}), 404

    db.session.delete(composicao)
    db.session.commit()
    return jsonify({"mensagem": "Composicao deletada com sucesso"}), 200


@bp.route("/upsert/familia/<int:familia_id>", methods=["PUT"])
def upsert_composicao_familiar_por_familia(familia_id):
    """Rota de upsert (criação ou atualização baseada em familia_id)."""
    data = request.get_json()
    existente = ComposicaoFamiliar.query.filter_by(familia_id=familia_id).first()
    if existente:
        composicao = composicao_schema.load(data, instance=existente, partial=True)
    else:
        data["familia_id"] = familia_id
        composicao = composicao_schema.load(data)
        db.session.add(composicao)
    db.session.commit()
    return composicao_schema.jsonify(composicao)

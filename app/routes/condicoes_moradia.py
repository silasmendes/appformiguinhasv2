from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models.condicoes_moradia import CondicaoMoradia
from app.schemas.condicoes_moradia import CondicaoMoradiaSchema
from app import db

bp = Blueprint("condicoes_moradia", __name__, url_prefix="/condicoes_moradia")

condicao_schema = CondicaoMoradiaSchema()
condicoes_schema = CondicaoMoradiaSchema(many=True)


@bp.route("", methods=["POST"])
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
def listar_condicoes_moradia():
    condicoes = CondicaoMoradia.query.all()
    return condicoes_schema.jsonify(condicoes), 200


@bp.route("/<int:moradia_id>", methods=["GET"])
def obter_condicao_moradia(moradia_id):
    condicao = db.session.get(CondicaoMoradia, moradia_id)
    if not condicao:
        return jsonify({"mensagem": "Condição de moradia não encontrada"}), 404
    return condicao_schema.jsonify(condicao)


@bp.route("/<int:moradia_id>", methods=["PUT"])
def atualizar_condicao_moradia(moradia_id):
    condicao = db.session.get(CondicaoMoradia, moradia_id)
    if not condicao:
        return jsonify({"mensagem": "Condição de moradia não encontrada"}), 404

    data = request.get_json()
    condicao = condicao_schema.load(data, instance=condicao, partial=True)

    db.session.commit()
    return condicao_schema.jsonify(condicao)


@bp.route("/<int:moradia_id>", methods=["DELETE"])
def deletar_condicao_moradia(moradia_id):
    condicao = db.session.get(CondicaoMoradia, moradia_id)
    if not condicao:
        return jsonify({"mensagem": "Condição de moradia não encontrada"}), 404

    db.session.delete(condicao)
    db.session.commit()
    return jsonify({"mensagem": "Condição de moradia deletada com sucesso"}), 200

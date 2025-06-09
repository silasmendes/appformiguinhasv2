from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models.educacao_entrevistado import EducacaoEntrevistado
from app.schemas.educacao_entrevistado import EducacaoEntrevistadoSchema
from app import db

bp = Blueprint("educacao_entrevistado", __name__, url_prefix="/educacao_entrevistado")

educacao_schema = EducacaoEntrevistadoSchema()
educacoes_schema = EducacaoEntrevistadoSchema(many=True)


@bp.route("", methods=["POST"])
def criar_educacao():
    data = request.get_json()
    try:
        nova_educacao = educacao_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(nova_educacao)
    db.session.commit()
    return educacao_schema.jsonify(nova_educacao), 201


@bp.route("", methods=["GET"])
def listar_educacoes():
    educacoes = EducacaoEntrevistado.query.all()
    return educacoes_schema.jsonify(educacoes), 200


@bp.route("/<int:educacao_id>", methods=["GET"])
def obter_educacao(educacao_id):
    educacao = db.session.get(EducacaoEntrevistado, educacao_id)
    if not educacao:
        return jsonify({"mensagem": "Educação do entrevistado não encontrada"}), 404
    return educacao_schema.jsonify(educacao)


@bp.route("/<int:educacao_id>", methods=["PUT"])
def atualizar_educacao(educacao_id):
    educacao = db.session.get(EducacaoEntrevistado, educacao_id)
    if not educacao:
        return jsonify({"mensagem": "Educação do entrevistado não encontrada"}), 404

    data = request.get_json()
    educacao = educacao_schema.load(data, instance=educacao, partial=True)

    db.session.commit()
    return educacao_schema.jsonify(educacao)


@bp.route("/<int:educacao_id>", methods=["DELETE"])
def deletar_educacao(educacao_id):
    educacao = db.session.get(EducacaoEntrevistado, educacao_id)
    if not educacao:
        return jsonify({"mensagem": "Educação do entrevistado não encontrada"}), 404

    db.session.delete(educacao)
    db.session.commit()
    return jsonify({"mensagem": "Educação do entrevistado deletada com sucesso"}), 200

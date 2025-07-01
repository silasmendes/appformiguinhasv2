from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.models.educacao_entrevistado import EducacaoEntrevistado
from app.schemas.educacao_entrevistado import EducacaoEntrevistadoSchema
from app import db

bp = Blueprint("educacao_entrevistado", __name__, url_prefix="/educacao_entrevistado")

educacao_schema = EducacaoEntrevistadoSchema()
educacoes_schema = EducacaoEntrevistadoSchema(many=True)


@bp.route("", methods=["POST"])
@jwt_required()
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
@jwt_required()
def listar_educacoes():
    educacoes = EducacaoEntrevistado.query.all()
    return educacoes_schema.jsonify(educacoes), 200


@bp.route("/<int:educacao_id>", methods=["GET"])
@jwt_required()
def obter_educacao(educacao_id):
    educacao = db.session.get(EducacaoEntrevistado, educacao_id)
    if not educacao:
        return jsonify({"mensagem": "Educação do entrevistado não encontrada"}), 404
    return educacao_schema.jsonify(educacao)


@bp.route("/<int:educacao_id>", methods=["PUT"])
@jwt_required()
def atualizar_educacao(educacao_id):
    educacao = db.session.get(EducacaoEntrevistado, educacao_id)
    if not educacao:
        return jsonify({"mensagem": "Educação do entrevistado não encontrada"}), 404

    data = request.get_json()
    educacao = educacao_schema.load(data, instance=educacao, partial=True)

    db.session.commit()
    return educacao_schema.jsonify(educacao)


@bp.route("/<int:educacao_id>", methods=["DELETE"])
@jwt_required()
def deletar_educacao(educacao_id):
    educacao = db.session.get(EducacaoEntrevistado, educacao_id)
    if not educacao:
        return jsonify({"mensagem": "Educação do entrevistado não encontrada"}), 404

    db.session.delete(educacao)
    db.session.commit()
    return jsonify({"mensagem": "Educação do entrevistado deletada com sucesso"}), 200


@bp.route("/upsert/familia/<int:familia_id>", methods=["PUT"])
@jwt_required()
def upsert_educacao_entrevistado_por_familia(familia_id):
    """Rota de upsert (criação ou atualização baseada em familia_id)."""
    data = request.get_json()
    existente = EducacaoEntrevistado.query.filter_by(familia_id=familia_id).first()
    if existente:
        educacao = educacao_schema.load(data, instance=existente, partial=True)
    else:
        data["familia_id"] = familia_id
        educacao = educacao_schema.load(data)
        db.session.add(educacao)
    db.session.commit()
    return educacao_schema.jsonify(educacao)

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.models.demanda_tipo import DemandaTipo
from app.schemas.demanda_tipo import DemandaTipoSchema
from app import db

bp = Blueprint("demanda_tipos", __name__, url_prefix="/demanda_tipos")

demanda_tipo_schema = DemandaTipoSchema()
demanda_tipos_schema = DemandaTipoSchema(many=True)

@bp.route("", methods=["POST"])
@jwt_required()
def criar_demanda_tipo():
    data = request.get_json()
    try:
        novo_tipo = demanda_tipo_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(novo_tipo)
    db.session.commit()
    return demanda_tipo_schema.jsonify(novo_tipo), 201

@bp.route("", methods=["GET"])
@jwt_required()
def listar_demanda_tipos():
    tipos = DemandaTipo.query.all()
    return demanda_tipos_schema.jsonify(tipos), 200

@bp.route("/<int:demanda_tipo_id>", methods=["GET"])
@jwt_required()
def obter_demanda_tipo(demanda_tipo_id):
    tipo = db.session.get(DemandaTipo, demanda_tipo_id)
    if not tipo:
        return jsonify({"mensagem": "Demanda tipo não encontrada"}), 404
    return demanda_tipo_schema.jsonify(tipo)

@bp.route("/<int:demanda_tipo_id>", methods=["PUT"])
@jwt_required()
def atualizar_demanda_tipo(demanda_tipo_id):
    tipo = db.session.get(DemandaTipo, demanda_tipo_id)
    if not tipo:
        return jsonify({"mensagem": "Demanda tipo não encontrada"}), 404

    data = request.get_json()
    tipo = demanda_tipo_schema.load(data, instance=tipo, partial=True)

    db.session.commit()
    return demanda_tipo_schema.jsonify(tipo)

@bp.route("/<int:demanda_tipo_id>", methods=["DELETE"])
@jwt_required()
def deletar_demanda_tipo(demanda_tipo_id):
    tipo = db.session.get(DemandaTipo, demanda_tipo_id)
    if not tipo:
        return jsonify({"mensagem": "Demanda tipo não encontrada"}), 404

    db.session.delete(tipo)
    db.session.commit()
    return jsonify({"mensagem": "Demanda tipo deletada com sucesso"}), 200

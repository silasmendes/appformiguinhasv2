from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.models.demanda_etapa import DemandaEtapa
from app.schemas.demanda_etapa import DemandaEtapaSchema
from app import db

bp = Blueprint("demanda_etapas", __name__, url_prefix="/demanda_etapas")

demanda_etapa_schema = DemandaEtapaSchema()
demanda_etapas_schema = DemandaEtapaSchema(many=True)

@bp.route("", methods=["POST"])
@jwt_required()
def criar_demanda_etapa():
    data = request.get_json()
    try:
        nova_etapa = demanda_etapa_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(nova_etapa)
    db.session.commit()
    return demanda_etapa_schema.jsonify(nova_etapa), 201

@bp.route("", methods=["GET"])
@jwt_required()
def listar_demanda_etapas():
    etapas = DemandaEtapa.query.all()
    return demanda_etapas_schema.jsonify(etapas), 200

@bp.route("/<int:etapa_id>", methods=["GET"])
@jwt_required()
def obter_demanda_etapa(etapa_id):
    etapa = db.session.get(DemandaEtapa, etapa_id)
    if not etapa:
        return jsonify({"mensagem": "Etapa não encontrada"}), 404
    return demanda_etapa_schema.jsonify(etapa)

@bp.route("/<int:etapa_id>", methods=["PUT"])
@jwt_required()
def atualizar_demanda_etapa(etapa_id):
    etapa = db.session.get(DemandaEtapa, etapa_id)
    if not etapa:
        return jsonify({"mensagem": "Etapa não encontrada"}), 404

    data = request.get_json()
    etapa = demanda_etapa_schema.load(data, instance=etapa, partial=True)

    db.session.commit()
    return demanda_etapa_schema.jsonify(etapa)

@bp.route("/<int:etapa_id>", methods=["DELETE"])
@jwt_required()
def deletar_demanda_etapa(etapa_id):
    etapa = db.session.get(DemandaEtapa, etapa_id)
    if not etapa:
        return jsonify({"mensagem": "Etapa não encontrada"}), 404

    db.session.delete(etapa)
    db.session.commit()
    return jsonify({"mensagem": "Etapa deletada com sucesso"}), 200

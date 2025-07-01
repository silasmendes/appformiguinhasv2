from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.models.atendimento import Atendimento
from app.schemas.atendimento import AtendimentoSchema
from app import db

bp = Blueprint("atendimentos", __name__, url_prefix="/atendimentos")

atendimento_schema = AtendimentoSchema()
atendimentos_schema = AtendimentoSchema(many=True)

@bp.route("", methods=["POST"])
@jwt_required()
def criar_atendimento():
    data = request.get_json()
    try:
        novo = atendimento_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    db.session.add(novo)
    db.session.commit()
    return atendimento_schema.jsonify(novo), 201

@bp.route("", methods=["GET"])
@jwt_required()
def listar_atendimentos():
    familia_id = request.args.get("familia_id")
    query = Atendimento.query
    if familia_id:
        query = query.filter_by(familia_id=familia_id)
    atendimentos = query.all()
    return atendimentos_schema.jsonify(atendimentos), 200

@bp.route("/<int:atendimento_id>", methods=["GET"])
@jwt_required()
def obter_atendimento(atendimento_id):
    atendimento = db.session.get(Atendimento, atendimento_id)
    if not atendimento:
        return jsonify({"mensagem": "Atendimento não encontrado"}), 404
    return atendimento_schema.jsonify(atendimento)

@bp.route("/<int:atendimento_id>", methods=["PUT"])
@jwt_required()
def atualizar_atendimento(atendimento_id):
    atendimento = db.session.get(Atendimento, atendimento_id)
    if not atendimento:
        return jsonify({"mensagem": "Atendimento não encontrado"}), 404
    data = request.get_json()
    try:
        atendimento = atendimento_schema.load(data, instance=atendimento, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400
    db.session.commit()
    return atendimento_schema.jsonify(atendimento)


from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.models.renda_familiar import RendaFamiliar
from app.schemas.renda_familiar import RendaFamiliarSchema
from app import db

bp = Blueprint("renda_familiar", __name__, url_prefix="/renda_familiar")

renda_schema = RendaFamiliarSchema()
rendas_schema = RendaFamiliarSchema(many=True)

@bp.route("", methods=["POST"])
@jwt_required()
def criar_renda():
    data = request.get_json()
    try:
        nova_renda = renda_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(nova_renda)
    db.session.commit()
    return renda_schema.jsonify(nova_renda), 201

@bp.route("", methods=["GET"])
@jwt_required()
def listar_rendas():
    rendas = RendaFamiliar.query.all()
    return rendas_schema.jsonify(rendas), 200

@bp.route("/<int:renda_id>", methods=["GET"])
@jwt_required()
def obter_renda(renda_id):
    renda = db.session.get(RendaFamiliar, renda_id)
    if not renda:
        return jsonify({"mensagem": "Renda familiar não encontrada"}), 404
    return renda_schema.jsonify(renda)

@bp.route("/<int:renda_id>", methods=["PUT"])
@jwt_required()
def atualizar_renda(renda_id):
    renda = db.session.get(RendaFamiliar, renda_id)
    if not renda:
        return jsonify({"mensagem": "Renda familiar não encontrada"}), 404

    data = request.get_json()
    renda = renda_schema.load(data, instance=renda, partial=True)

    db.session.commit()
    return renda_schema.jsonify(renda)

@bp.route("/<int:renda_id>", methods=["DELETE"])
@jwt_required()
def deletar_renda(renda_id):
    renda = db.session.get(RendaFamiliar, renda_id)
    if not renda:
        return jsonify({"mensagem": "Renda familiar não encontrada"}), 404

    db.session.delete(renda)
    db.session.commit()
    return jsonify({"mensagem": "Renda familiar deletada com sucesso"}), 200


@bp.route("/upsert/familia/<int:familia_id>", methods=["PUT"])
@jwt_required()
def upsert_renda_familiar_por_familia(familia_id):
    """Rota de upsert (criação ou atualização baseada em familia_id)."""
    data = request.get_json()
    existente = RendaFamiliar.query.filter_by(familia_id=familia_id).first()
    if existente:
        renda = renda_schema.load(data, instance=existente, partial=True)
    else:
        data["familia_id"] = familia_id
        renda = renda_schema.load(data)
        db.session.add(renda)
    db.session.commit()
    return renda_schema.jsonify(renda)

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.models.saude_familiar import SaudeFamiliar
from app.schemas.saude_familiar import SaudeFamiliarSchema
from app import db

bp = Blueprint("saude_familiar", __name__, url_prefix="/saude_familiar")

saude_schema = SaudeFamiliarSchema()
saudes_schema = SaudeFamiliarSchema(many=True)

@bp.route("", methods=["POST"])
@jwt_required()
def criar_saude():
    data = request.get_json()
    try:
        nova_saude = saude_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(nova_saude)
    db.session.commit()
    return saude_schema.jsonify(nova_saude), 201

@bp.route("", methods=["GET"])
@jwt_required()
def listar_saudes():
    saudes = SaudeFamiliar.query.all()
    return saudes_schema.jsonify(saudes), 200

@bp.route("/<int:saude_id>", methods=["GET"])
@jwt_required()
def obter_saude(saude_id):
    saude = db.session.get(SaudeFamiliar, saude_id)
    if not saude:
        return jsonify({"mensagem": "Saude familiar não encontrada"}), 404
    return saude_schema.jsonify(saude)

@bp.route("/<int:saude_id>", methods=["PUT"])
@jwt_required()
def atualizar_saude(saude_id):
    saude = db.session.get(SaudeFamiliar, saude_id)
    if not saude:
        return jsonify({"mensagem": "Saude familiar não encontrada"}), 404

    data = request.get_json()
    saude = saude_schema.load(data, instance=saude, partial=True)

    db.session.commit()
    return saude_schema.jsonify(saude)

@bp.route("/<int:saude_id>", methods=["DELETE"])
@jwt_required()
def deletar_saude(saude_id):
    saude = db.session.get(SaudeFamiliar, saude_id)
    if not saude:
        return jsonify({"mensagem": "Saude familiar não encontrada"}), 404

    db.session.delete(saude)
    db.session.commit()
    return jsonify({"mensagem": "Saude familiar deletada com sucesso"}), 200


@bp.route("/upsert/familia/<int:familia_id>", methods=["PUT"])
@jwt_required()
def upsert_saude_familiar_por_familia(familia_id):
    """Rota de upsert (criação ou atualização baseada em familia_id)."""
    data = request.get_json()
    existente = SaudeFamiliar.query.filter_by(familia_id=familia_id).first()
    if existente:
        saude = saude_schema.load(data, instance=existente, partial=True)
    else:
        data["familia_id"] = familia_id
        saude = saude_schema.load(data)
        db.session.add(saude)
    db.session.commit()
    return saude_schema.jsonify(saude)

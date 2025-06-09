from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models.familia import Familia
from app.schemas.familia import FamiliaSchema
from app import db

bp = Blueprint("familias", __name__, url_prefix="/familias")

familia_schema = FamiliaSchema()
familias_schema = FamiliaSchema(many=True)

@bp.route("", methods=["POST"])
def criar_familia():
    data = request.get_json()
    try:
        nova_familia = familia_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    db.session.add(nova_familia)
    db.session.commit()
    return familia_schema.jsonify(nova_familia), 201

@bp.route("", methods=["GET"])
def listar_familias():
    familias = Familia.query.all()
    return familias_schema.jsonify(familias), 200

@bp.route("/<int:familia_id>", methods=["GET"])
def obter_familia(familia_id):
    familia = db.session.get(Familia, familia_id)
    if not familia:
        return jsonify({"mensagem": "Família não encontrada"}), 404
    return familia_schema.jsonify(familia)

@bp.route("/<int:familia_id>", methods=["PUT"])
def atualizar_familia(familia_id):
    familia = db.session.get(Familia, familia_id)
    if not familia:
        return jsonify({"mensagem": "Família não encontrada"}), 404

    data = request.get_json()
    familia = familia_schema.load(data, instance=familia, partial=True)

    db.session.commit()
    return familia_schema.jsonify(familia)

@bp.route("/<int:familia_id>", methods=["DELETE"])
def deletar_familia(familia_id):
    familia = db.session.get(Familia, familia_id)
    if not familia:
        return jsonify({"mensagem": "Família não encontrada"}), 404

    db.session.delete(familia)
    db.session.commit()
    return jsonify({"mensagem": "Família deletada com sucesso"}), 200

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models.emprego_provedor import EmpregoProvedor
from app.schemas.emprego_provedor import EmpregoProvedorSchema
from app import db

bp = Blueprint("emprego_provedor", __name__, url_prefix="/emprego_provedor")

emprego_schema = EmpregoProvedorSchema()
empregos_schema = EmpregoProvedorSchema(many=True)

@bp.route("", methods=["POST"])
def criar_emprego():
    data = request.get_json()
    try:
        novo_emprego = emprego_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(novo_emprego)
    db.session.commit()
    return emprego_schema.jsonify(novo_emprego), 201

@bp.route("", methods=["GET"])
def listar_empregos():
    empregos = EmpregoProvedor.query.all()
    return empregos_schema.jsonify(empregos), 200

@bp.route("/<int:emprego_id>", methods=["GET"])
def obter_emprego(emprego_id):
    emprego = db.session.get(EmpregoProvedor, emprego_id)
    if not emprego:
        return jsonify({"mensagem": "Emprego provedor não encontrado"}), 404
    return emprego_schema.jsonify(emprego)

@bp.route("/<int:emprego_id>", methods=["PUT"])
def atualizar_emprego(emprego_id):
    emprego = db.session.get(EmpregoProvedor, emprego_id)
    if not emprego:
        return jsonify({"mensagem": "Emprego provedor não encontrado"}), 404

    data = request.get_json()
    emprego = emprego_schema.load(data, instance=emprego, partial=True)

    db.session.commit()
    return emprego_schema.jsonify(emprego)

@bp.route("/<int:emprego_id>", methods=["DELETE"])
def deletar_emprego(emprego_id):
    emprego = db.session.get(EmpregoProvedor, emprego_id)
    if not emprego:
        return jsonify({"mensagem": "Emprego provedor não encontrado"}), 404

    db.session.delete(emprego)
    db.session.commit()
    return jsonify({"mensagem": "Emprego provedor deletado com sucesso"}), 200

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models.endereco import Endereco
from app.schemas.endereco import EnderecoSchema
from app import db

bp = Blueprint("enderecos", __name__, url_prefix="/enderecos")

endereco_schema = EnderecoSchema()
enderecos_schema = EnderecoSchema(many=True)

@bp.route("", methods=["POST"])
def criar_endereco():
    data = request.get_json()
    try:
        novo_endereco = endereco_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(novo_endereco)
    db.session.commit()
    return endereco_schema.jsonify(novo_endereco), 201

@bp.route("", methods=["GET"])
def listar_enderecos():
    enderecos = Endereco.query.all()
    return enderecos_schema.jsonify(enderecos), 200

@bp.route("/<int:endereco_id>", methods=["GET"])
def obter_endereco(endereco_id):
    endereco = db.session.get(Endereco, endereco_id)
    if not endereco:
        return jsonify({"mensagem": "Endereço não encontrado"}), 404
    return endereco_schema.jsonify(endereco)

@bp.route("/<int:endereco_id>", methods=["PUT"])
def atualizar_endereco(endereco_id):
    endereco = db.session.get(Endereco, endereco_id)
    if not endereco:
        return jsonify({"mensagem": "Endereço não encontrado"}), 404

    data = request.get_json()
    endereco = endereco_schema.load(data, instance=endereco, partial=True)

    db.session.commit()
    return endereco_schema.jsonify(endereco)

@bp.route("/<int:endereco_id>", methods=["DELETE"])
def deletar_endereco(endereco_id):
    endereco = db.session.get(Endereco, endereco_id)
    if not endereco:
        return jsonify({"mensagem": "Endereço não encontrado"}), 404

    db.session.delete(endereco)
    db.session.commit()
    return jsonify({"mensagem": "Endereço deletado com sucesso"}), 200

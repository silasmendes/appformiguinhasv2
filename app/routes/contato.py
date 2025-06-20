from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models.contato import Contato
from app.schemas.contato import ContatoSchema
from app import db

bp = Blueprint("contatos", __name__, url_prefix="/contatos")

contato_schema = ContatoSchema()
contatos_schema = ContatoSchema(many=True)


@bp.route("", methods=["POST"])
def criar_contato():
    data = request.get_json()
    try:
        novo_contato = contato_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(novo_contato)
    db.session.commit()
    return contato_schema.jsonify(novo_contato), 201


@bp.route("", methods=["GET"])
def listar_contatos():
    contatos = Contato.query.all()
    return contatos_schema.jsonify(contatos), 200


@bp.route("/<int:contato_id>", methods=["GET"])
def obter_contato(contato_id):
    contato = db.session.get(Contato, contato_id)
    if not contato:
        return jsonify({"mensagem": "Contato não encontrado"}), 404
    return contato_schema.jsonify(contato)


@bp.route("/<int:contato_id>", methods=["PUT"])
def atualizar_contato(contato_id):
    contato = db.session.get(Contato, contato_id)
    if not contato:
        return jsonify({"mensagem": "Contato não encontrado"}), 404

    data = request.get_json()
    contato = contato_schema.load(data, instance=contato, partial=True)

    db.session.commit()
    return contato_schema.jsonify(contato)


@bp.route("/upsert/familia/<int:familia_id>", methods=["PUT"])
def upsert_contato_por_familia(familia_id):
    """Rota de upsert (criação ou atualização baseada em familia_id)."""
    data = request.get_json()
    existente = Contato.query.filter_by(familia_id=familia_id).first()
    if existente:
        contato = contato_schema.load(data, instance=existente, partial=True)
    else:
        data["familia_id"] = familia_id
        contato = contato_schema.load(data)
        db.session.add(contato)
    db.session.commit()
    return contato_schema.jsonify(contato)


@bp.route("/<int:contato_id>", methods=["DELETE"])
def deletar_contato(contato_id):
    contato = db.session.get(Contato, contato_id)
    if not contato:
        return jsonify({"mensagem": "Contato não encontrado"}), 404

    db.session.delete(contato)
    db.session.commit()
    return jsonify({"mensagem": "Contato deletado com sucesso"}), 200

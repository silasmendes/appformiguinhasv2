from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.models.demanda_familia import DemandaFamilia
from app.schemas.demanda_familia import DemandaFamiliaSchema
from app import db

bp = Blueprint("demandas", __name__, url_prefix="/demandas")

demanda_schema = DemandaFamiliaSchema()
demandas_schema = DemandaFamiliaSchema(many=True)

@bp.route("", methods=["POST"])
def criar_demanda():
    data = request.get_json()
    try:
        nova_demanda = demanda_schema.load(data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(nova_demanda)
    db.session.commit()
    return demanda_schema.jsonify(nova_demanda), 201

@bp.route("", methods=["GET"])
def listar_demandas():
    demandas = DemandaFamilia.query.all()
    return demandas_schema.jsonify(demandas), 200

@bp.route("/<int:demanda_id>", methods=["GET"])
def obter_demanda(demanda_id):
    demanda = db.session.get(DemandaFamilia, demanda_id)
    if not demanda:
        return jsonify({"mensagem": "Demanda não encontrada"}), 404
    return demanda_schema.jsonify(demanda)

@bp.route("/<int:demanda_id>", methods=["PUT"])
def atualizar_demanda(demanda_id):
    demanda = db.session.get(DemandaFamilia, demanda_id)
    if not demanda:
        return jsonify({"mensagem": "Demanda não encontrada"}), 404

    data = request.get_json()
    demanda = demanda_schema.load(data, instance=demanda, partial=True)

    db.session.commit()
    return demanda_schema.jsonify(demanda)

@bp.route("/<int:demanda_id>", methods=["DELETE"])
def deletar_demanda(demanda_id):
    demanda = db.session.get(DemandaFamilia, demanda_id)
    if not demanda:
        return jsonify({"mensagem": "Demanda não encontrada"}), 404

    db.session.delete(demanda)
    db.session.commit()
    return jsonify({"mensagem": "Demanda deletada com sucesso"}), 200


@bp.route("/upsert/lote/familia/<int:familia_id>", methods=["PUT"])
def upsert_demandas_familia(familia_id):
    dados = request.get_json()
    if not isinstance(dados, list):
        return jsonify({"erro": "Esperado uma lista de demandas"}), 400

    demandas_salvas = []

    try:
        for entrada in dados:
            demanda_id = entrada.get("demanda_id")
            entrada["familia_id"] = familia_id  # reforça vínculo correto

            if demanda_id:
                demanda = db.session.get(DemandaFamilia, demanda_id)
                if demanda and demanda.familia_id == familia_id:
                    demanda = demanda_schema.load(entrada, instance=demanda, partial=True)
                else:
                    continue  # ignora se não pertencer à família ou não encontrado
            else:
                demanda = demanda_schema.load(entrada)
                db.session.add(demanda)

            demandas_salvas.append(demanda)

        db.session.commit()
        return demandas_schema.jsonify(demandas_salvas), 200

    except ValidationError as e:
        db.session.rollback()
        return jsonify({"erro": "Erro de validação", "detalhes": e.messages}), 400
    except Exception as ex:
        db.session.rollback()
        print(f"Erro inesperado no upsert de demandas: {ex}")
        return jsonify({"erro": "Erro interno ao salvar demandas"}), 500


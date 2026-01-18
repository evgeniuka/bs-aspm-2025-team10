from flask import Blueprint, jsonify

from utils.jwt_utils import role_required, token_required

clients_bp = Blueprint("clients", __name__)


@clients_bp.route("/api/clients", methods=["GET"])
@token_required
@role_required("trainer")
def get_clients():
    return jsonify({"clients": []}), 200

from flask import Blueprint

bp = Blueprint('errors', __name__)

from wansink_partner.errors import handlers

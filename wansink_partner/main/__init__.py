from flask import Blueprint

bp = Blueprint('main', __name__)

from wansink_partner.main import routes

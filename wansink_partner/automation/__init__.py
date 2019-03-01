from flask import Blueprint

bp = Blueprint('automation', __name__)

from wansink_partner.automation import routes

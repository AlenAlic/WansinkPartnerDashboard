from wansink_partner import login, Anonymous, db
from flask import current_app, url_for, redirect, flash, Response, request
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from time import time
import jwt
from wansink_partner.values import *
from datetime import datetime


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def requires_access_level(access_levels):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.access not in access_levels:
                flash("Page inaccessible.")
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.args.get("Auth-Key") != current_app.config.get('AUTH_KEY'):
            return Response(status=403)
        return f(*args, **kwargs)
    return decorated_function


class User(UserMixin, Anonymous, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    access = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'{self.username}'

    def get_id(self):
        return self.user_id

    def is_admin(self):
        return self.access == ACCESS[ADMIN]

    def is_user(self):
        return self.access == ACCESS[USER]

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.user_id, 'exp': time() + expires_in},
                          current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except jwt.exceptions.InvalidTokenError:
            return 'error'
        return User.query.get(user_id)


class Authentication(db.Model):
    __tablename__ = 'auth_tokens'
    lock = db.Column(db.Integer, primary_key=True)
    trello_key = db.Column(db.String(512))
    trello_token = db.Column(db.String(512))
    simplicate_key = db.Column(db.String(512))
    simplicate_secret = db.Column(db.String(512))

    def __repr__(self):
        return 'Authentication Keys'


class Jaarwerk(db.Model):
    __tablename__ = 'jaarwerk'
    lock = db.Column(db.Integer, primary_key=True)
    source_board_name = db.Column(db.String(256))
    source_board_id = db.Column(db.String(256))
    target_board_name = db.Column(db.String(256))
    target_board_id = db.Column(db.String(256))
    target_list_name = db.Column(db.String(256))
    target_list_id = db.Column(db.String(256))

    def __repr__(self):
        return 'Jaarwerk automatisering'


class JaarwerkResult(db.Model):
    __tablename__ = 'jaarwerk_result'
    archive_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    result = db.Column(db.Text())


class Maandwerk(db.Model):
    __tablename__ = 'maandwerk'
    lock = db.Column(db.Integer, primary_key=True)
    source_board_name = db.Column(db.String(256))
    source_board_id = db.Column(db.String(256))
    source_list_month_name = db.Column(db.String(256))
    source_list_month_id = db.Column(db.String(256))
    source_list_quarter_name = db.Column(db.String(256))
    source_list_quarter_id = db.Column(db.String(256))
    target_board_name = db.Column(db.String(256))
    target_board_id = db.Column(db.String(256))
    source_list_name = db.Column(db.String(256))
    source_list_id = db.Column(db.String(256))
    target_list_name = db.Column(db.String(256))
    target_list_id = db.Column(db.String(256))

    def __repr__(self):
        return 'Maandwerk automatisering'


class MaandwerkCopyResult(db.Model):
    __tablename__ = 'maandwerk_copy_result'
    archive_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    result = db.Column(db.Text())


class MaandwerkMoveResult(db.Model):
    __tablename__ = 'maandwerk_move_result'
    archive_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    result = db.Column(db.Text())


class KlaarArchiefLinks(db.Model):
    __tablename__ = 'klaar_archief_links'
    __table_args__ = (db.UniqueConstraint('source_id', 'target_id', name='_source_target_uc'),)
    link_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    source_id = db.Column(db.String(256))
    source_name = db.Column(db.String(256))
    target_id = db.Column(db.String(256))
    target_name = db.Column(db.String(256))
    board_id = db.Column(db.String(256))
    board_name = db.Column(db.String(256))

    def __repr__(self):
        return f"Klaar Archief voor {self.name}"


class KlaarArchiefResult(db.Model):
    __tablename__ = 'klaar_archief_result'
    archive_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    result = db.Column(db.Text())
    name = db.Column(db.Text())


class Employees(db.Model):
    __tablename__ = 'employees'
    employee_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(256), nullable=False)
    trello_id = db.Column(db.String(512), unique=True, nullable=False)
    simplicate_id = db.Column(db.String(512), unique=True, nullable=False)

    def __repr__(self):
        return self.full_name


class SimplicateTrelloCodes(db.Model):
    __tablename__ = 'simplicate_trello_codes'
    code_id = db.Column(db.Integer, primary_key=True)
    simplicate_code = db.Column(db.String(12))
    simplicate_id = db.Column(db.String(256))
    monthly = db.Column(db.Boolean, nullable=False, default=False)
    quarterly = db.Column(db.Boolean, nullable=False, default=False)
    yearly = db.Column(db.Boolean, nullable=False, default=False)
    jaarwerk = db.Column(db.Boolean, nullable=False, default=False)
    trello_code = db.Column(db.String(24))

    def __repr__(self):
        return f"{self.simplicate_code} - {self.trello_code}"


class ProjectTrelloCards(db.Model):
    __tablename__ = 'project_trello_cards'
    lock = db.Column(db.Integer, primary_key=True)
    planning_periodiek_werk_board_name = db.Column(db.String(256))
    planning_periodiek_werk_board_id = db.Column(db.String(256))
    planning_jaarwerk_board_name = db.Column(db.String(256))
    planning_jaarwerk_board_id = db.Column(db.String(256))
    nog_te_plannen_board_name = db.Column(db.String(256))
    nog_te_plannen_board_id = db.Column(db.String(256))
    month_list_name = db.Column(db.String(256))
    month_list_id = db.Column(db.String(256))
    quarter_list_name = db.Column(db.String(256))
    quarter_list_id = db.Column(db.String(256))
    year_list_name = db.Column(db.String(256))
    year_list_id = db.Column(db.String(256))
    afspraken_planning_volgend_jaar_list_name = db.Column(db.String(256))
    afspraken_planning_volgend_jaar_list_id = db.Column(db.String(256))
    exception_list_name = db.Column(db.String(256))
    exception_list_id = db.Column(db.String(256))
    periodiek_sjablonen_list_name = db.Column(db.String(256))
    periodiek_sjablonen_list_id = db.Column(db.String(256))
    jaarwerk_sjablonen_list_name = db.Column(db.String(256))
    jaarwerk_sjablonen_list_id = db.Column(db.String(256))
    periodiek_sjablonen_card_name = db.Column(db.String(256))
    periodiek_sjablonen_card_id = db.Column(db.String(256))
    jaarwerk_sjablonen_card_name = db.Column(db.String(256))
    jaarwerk_sjablonen_card_id = db.Column(db.String(256))

    def __repr__(self):
        return 'Project Trello kaarten automatisering'


class ProjectTrelloResults(db.Model):
    __tablename__ = 'project_trello_results'
    archive_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    project_id = db.Column(db.String(256))
    name = db.Column(db.String(256))
    link = db.Column(db.String(512))
    cards = db.relationship('ProjectTrelloResultsCard', back_populates='result', cascade='all, delete-orphan')

    def __repr__(self):
        return self.name


class ProjectTrelloResultsCard(db.Model):
    __tablename__ = 'project_trello_results_card'
    result_card_id = db.Column(db.Integer, primary_key=True)
    archive_id = db.Column(db.Integer, db.ForeignKey('project_trello_results.archive_id'))
    result = db.relationship('ProjectTrelloResults', back_populates='cards')
    board_id = db.Column(db.String(256))
    board_name = db.Column(db.String(256))
    list_id = db.Column(db.String(256))
    list_name = db.Column(db.String(256))
    card_id = db.Column(db.String(256))
    card_name = db.Column(db.String(256))
    card_desc = db.Column(db.String(1024))
    card_link = db.Column(db.String(512))

    def __repr__(self):
        return self.card_name

    def card_desc_with_link(self):
        return self.card_desc.replace(self.result.link,
                                      f'<a class="text-white" target="_blank" '
                                      f'href="{self.result.link}">{self.result.link}</a>')

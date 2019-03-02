from flask import Flask, redirect, url_for, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, AnonymousUserMixin
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail
from wtforms import PasswordField
import wansink_partner.values as values
from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy


# noinspection PyRedeclaration,PyArgumentList
class SQLAlchemy(_BaseSQLAlchemy):
    def apply_pool_defaults(self, app, options):
        super(SQLAlchemy, self).apply_pool_defaults(self, app, options)
        options["pool_pre_ping"] = True


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('main.index'))
        else:
            return self.render(self._template)


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
admin = Admin(template_mode='bootstrap3', index_view=MyAdminIndexView())
mail = Mail()


class BaseView(ModelView):
    column_hide_backrefs = False
    page_size = 100

    def is_accessible(self):
        if current_user.is_authenticated:
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.index'))


class UserView(BaseView):
    column_exclude_list = ['password_hash', ]
    form_excluded_columns = ['password_hash', ]
    form_extra_fields = {'password2': PasswordField('Password')}

    # noinspection PyPep8Naming
    def on_model_change(self, form, User, is_created):
        if form.password2.data != '':
            User.set_password(form.password2.data)


class Anonymous(AnonymousUserMixin):
    @staticmethod
    def is_admin():
        return False

    @staticmethod
    def is_user():
        return False


def create_app():
    from wansink_partner.models import User, Authentication, Jaarwerk, JaarwerkResult, Maandwerk, MaandwerkCopyResult, \
        MaandwerkMoveResult, KlaarArchiefLinks, KlaarArchiefResult, Employees, SimplicateTrelloCodes, \
        ProjectTrelloCards, ProjectTrelloResults, ProjectTrelloResultsCard
    from wansink_partner.funtions import trello_request, simplicate_request

    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py')
    app.url_map.strict_slashes = False

    # Init add-ons
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite:'))
    login.init_app(app)
    login.login_view = 'main.index'
    login.anonymous_user = Anonymous
    mail.init_app(app)
    admin.init_app(app)
    admin.add_view(UserView(User, db.session))
    admin.add_view(BaseView(Authentication, db.session))
    admin.add_view(BaseView(Jaarwerk, db.session))
    admin.add_view(BaseView(JaarwerkResult, db.session))
    admin.add_view(BaseView(Maandwerk, db.session))
    admin.add_view(BaseView(MaandwerkCopyResult, db.session))
    admin.add_view(BaseView(MaandwerkMoveResult, db.session))
    admin.add_view(BaseView(KlaarArchiefLinks, db.session))
    admin.add_view(BaseView(KlaarArchiefResult, db.session))
    admin.add_view(BaseView(Employees, db.session))
    admin.add_view(BaseView(SimplicateTrelloCodes, db.session))
    admin.add_view(BaseView(ProjectTrelloCards, db.session))
    admin.add_view(BaseView(ProjectTrelloResults, db.session))
    admin.add_view(BaseView(ProjectTrelloResultsCard, db.session))

    # Shell command for admin account
    def create_admin(admin_password):
        with app.app_context():
            user = User()
            user.username = 'admin'
            user.set_password(admin_password)
            user.is_active = True
            user.access = values.ACCESS[values.ADMIN]
            db.session.add(user)
            db.session.commit()
            db.session.add(Authentication())
            db.session.add(Jaarwerk())
            db.session.add(Maandwerk())
            db.session.add(ProjectTrelloCards())
            db.session.commit()
            generate_auth()

    # Shell command
    def generate_auth():
        with app.app_context():
            auth = Authentication.query.first()
            auth.trello_key = app.config.get('TRELLO_KEY')
            auth.trello_token = app.config.get('TRELLO_TOKEN')
            auth.simplicate_key = app.config.get('SIMPLICATE_KEY')
            auth.simplicate_secret = app.config.get('SIMPLICATE_SECRET')
            db.session.commit()

    # Shell command
    def create_development_environment():
        with app.app_context():
            KlaarArchiefLinks.query.delete()
            SimplicateTrelloCodes.query.delete()
            db.session.commit()
            generate_auth()
            jw = Jaarwerk.query.first()
            source_board = trello_request(api=("boards", app.config.get('PLANNING_JAARWERK')))
            target_board = trello_request(api=("boards", app.config.get('JAARWERK_SAM_VJV')))
            target_list = trello_request(api=("lists", app.config.get('NOG_TE_STARTEN')))
            jw.source_board_id = source_board["id"]
            jw.source_board_name = source_board["name"]
            jw.target_board_id = target_board["id"]
            jw.target_board_name = target_board["name"]
            jw.target_list_id = target_list["id"]
            jw.target_list_name = target_list["name"]
            db.session.commit()
            mw = Maandwerk.query.first()
            source_board = trello_request(api=("boards", app.config.get('PLANNING_PERIODIEK_WERK')))
            source_list_month = trello_request(api=("lists", app.config.get('MAAND')))
            source_list_quarter = trello_request(api=("lists", app.config.get('KWARTAAL')))
            target_board = trello_request(api=("boards", app.config.get('MAANDWERK')))
            source_list = trello_request(api=("lists", app.config.get('TODO_VOLGENDE_MAAND')))
            target_list = trello_request(api=("lists", app.config.get('TODO_DEZE_MAAND')))
            mw.source_board_id = source_board["id"]
            mw.source_board_name = source_board["name"]
            mw.source_list_month_id = source_list_month["id"]
            mw.source_list_month_name = source_list_month["name"]
            mw.source_list_quarter_id = source_list_quarter["id"]
            mw.source_list_quarter_name = source_list_quarter["name"]
            mw.target_board_id = target_board["id"]
            mw.target_board_name = target_board["name"]
            mw.source_list_id = source_list["id"]
            mw.source_list_name = source_list["name"]
            mw.target_list_id = target_list["id"]
            mw.target_list_name = target_list["name"]
            db.session.commit()
            link = KlaarArchiefLinks()
            source_list = trello_request(api=("lists", app.config.get('JAARWERK_SAM_VJV_KLAAR')))
            target_list = trello_request(api=("lists", app.config.get('JAARWERK_SAM_VJV_ARCHIEF')))
            board = trello_request(api=("boards", target_list["idBoard"]))
            link.source_id = source_list["id"]
            link.source_name = source_list["name"]
            link.target_id = target_list["id"]
            link.target_name = target_list["name"]
            link.board_id = board["id"]
            link.board_name = board["name"]
            db.session.add(link)
            db.session.commit()
            link = KlaarArchiefLinks()
            source_list = trello_request(api=("lists", app.config.get('MAANDWERK_KLAAR')))
            target_list = trello_request(api=("lists", app.config.get('MAANDWERK_ARCHIEF')))
            board = trello_request(api=("boards", target_list["idBoard"]))
            link.source_id = source_list["id"]
            link.source_name = source_list["name"]
            link.target_id = target_list["id"]
            link.target_name = target_list["name"]
            link.board_id = board["id"]
            link.board_name = board["name"]
            db.session.add(link)
            db.session.commit()
            for code in app.config.get('CODES_LINK'):
                c = SimplicateTrelloCodes()
                c.simplicate_code = code["simplicate_code"]
                c.simplicate_id = code["simplicate_id"]
                c.trello_code = code["trello_code"]
                c.monthly = code["monthly"]
                c.quarterly = code["quarterly"]
                c.yearly = code["yearly"]
                c.jaarwerk = code["jaarwerk"]
                db.session.add(c)
            db.session.commit()
            ptc = ProjectTrelloCards.query.first()
            planning_periodiek_werk_board = trello_request(api=("boards", app.config.get('PLANNING_PERIODIEK_WERK')))
            planning_jaarwerk_board = trello_request(api=("boards", app.config.get('PLANNING_JAARWERK')))
            nog_te_plannen_board = trello_request(api=("boards", app.config.get('NOG_TE_PLANNEN')))
            month_list = trello_request(api=("lists", app.config.get('MAAND')))
            quarter_list = trello_request(api=("lists", app.config.get('KWARTAAL')))
            year_list = trello_request(api=("lists", app.config.get('JAAR')))
            afspraken_planning_volgend_jaar_list = \
                trello_request(api=("lists", app.config.get('AFSPRAKEN_PLANNING_VOLGEND_JAAR')))
            exception_list = trello_request(api=("lists", app.config.get('SIMPLICATE_UITZONDERINGEN')))
            periodiek_sjablonen_list = trello_request(api=("lists", app.config.get('PERIODIEK_SJABLONEN_LIST')))
            jaarwerk_sjablonen_list = trello_request(api=("lists", app.config.get('JAARWERK_SJABLONEN_LIST')))
            periodiek_sjablonen_card = trello_request(api=("cards", app.config.get('PERIODIEK_SJABLONEN_CARD')))
            jaarwerk_sjablonen_card = trello_request(api=("cards", app.config.get('JAARWERK_SJABLONEN_CARD')))
            ptc.planning_periodiek_werk_board_id = planning_periodiek_werk_board["id"]
            ptc.planning_periodiek_werk_board_name = planning_periodiek_werk_board["name"]
            ptc.planning_jaarwerk_board_id = planning_jaarwerk_board["id"]
            ptc.planning_jaarwerk_board_name = planning_jaarwerk_board["name"]
            ptc.nog_te_plannen_board_id = nog_te_plannen_board["id"]
            ptc.nog_te_plannen_board_name = nog_te_plannen_board["name"]
            ptc.month_list_id = month_list["id"]
            ptc.month_list_name = month_list["name"]
            ptc.quarter_list_id = quarter_list["id"]
            ptc.quarter_list_name = quarter_list["name"]
            ptc.year_list_id = year_list["id"]
            ptc.year_list_name = year_list["name"]
            ptc.afspraken_planning_volgend_jaar_list_id = afspraken_planning_volgend_jaar_list["id"]
            ptc.afspraken_planning_volgend_jaar_list_name = afspraken_planning_volgend_jaar_list["name"]
            ptc.exception_list_id = exception_list["id"]
            ptc.exception_list_name = exception_list["name"]
            ptc.periodiek_sjablonen_list_id = periodiek_sjablonen_list["id"]
            ptc.periodiek_sjablonen_list_name = periodiek_sjablonen_list["name"]
            ptc.jaarwerk_sjablonen_list_id = jaarwerk_sjablonen_list["id"]
            ptc.jaarwerk_sjablonen_list_name = jaarwerk_sjablonen_list["name"]
            ptc.periodiek_sjablonen_card_id = periodiek_sjablonen_card["id"]
            ptc.periodiek_sjablonen_card_name = periodiek_sjablonen_card["name"]
            ptc.jaarwerk_sjablonen_card_id = jaarwerk_sjablonen_card["id"]
            ptc.jaarwerk_sjablonen_card_name = jaarwerk_sjablonen_card["name"]
            db.session.commit()

    @app.shell_context_processor
    def make_shell_context():
        return {'create_admin': create_admin, 'auth': generate_auth, 'dev': create_development_environment}

    @app.before_request
    def before_request_callback():
        g.auth = Authentication.query.first()

    # Register blueprints
    from wansink_partner.main import bp as main_bp
    app.register_blueprint(main_bp)

    from wansink_partner.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from wansink_partner.automation import bp as automation_bp
    app.register_blueprint(automation_bp, url_prefix='/automation')

    return app


from wansink_partner import models

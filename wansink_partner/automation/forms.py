from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired
from wansink_partner.values import *


class SwitchUserForm(FlaskForm):
    user = SelectField('Account', validators=[DataRequired()], coerce=int)
    submit = SubmitField('Switch account')


class EmployeeForm(FlaskForm):
    full_name = StringField('Naam', validators=[DataRequired()])
    trello_id = StringField('Trello id', validators=[DataRequired()])
    simplicate_id = StringField('Simplicate id', validators=[DataRequired()])
    employee_submit = SubmitField('Maak link')


class JaarwerkForm(FlaskForm):
    def __init__(self, jw=None, **kwargs):
        super().__init__(**kwargs)
        if jw is not None and request.method == GET:
            self.source_board_id.data = jw.source_board_id
            self.target_board_id.data = jw.target_board_id
            self.target_list_id.data = jw.target_list_id

    source_board_id = StringField('ID Planning Jaarwerk', validators=[DataRequired()])
    target_board_id = StringField('ID Jaarwerk SAM / VJV', validators=[DataRequired()])
    target_list_id = StringField('ID Nog te starten', validators=[DataRequired()])
    jaarwerk_submit = SubmitField('Sla wijzigingen op')


class MaandwerkForm(FlaskForm):
    def __init__(self, mw=None, **kwargs):
        super().__init__(**kwargs)
        if mw is not None and request.method == GET:
            self.source_board_id.data = mw.source_board_id
            self.source_list_month_id.data = mw.source_list_month_id
            self.source_list_quarter_id.data = mw.source_list_quarter_id
            self.target_board_id.data = mw.target_board_id
            self.source_list_id.data = mw.source_list_id
            self.target_list_id.data = mw.target_list_id

    source_board_id = StringField('ID Planning Periodiek werk', validators=[DataRequired()])
    source_list_month_id = StringField('ID Maand', validators=[DataRequired()])
    source_list_quarter_id = StringField('ID Kwartaal', validators=[DataRequired()])
    target_board_id = StringField('ID Maandwerk', validators=[DataRequired()])
    source_list_id = StringField('ID Todo volgende maand', validators=[DataRequired()])
    target_list_id = StringField('ID Todo deze maand', validators=[DataRequired()])
    maandwerk_submit = SubmitField('Sla wijzigingen op')


class GenerateEmployeeLinksForm(FlaskForm):
    generate_employee_links_submit = SubmitField('Maak automatisch links aan')


class ImportListsAndBoardsForm(FlaskForm):
    generate_employee_links_submit = SubmitField('Importeer Lists en Boards uit Trello')


class KlaarArchiefLinkForm(FlaskForm):
    source_list_id = StringField('ID Klaar', validators=[DataRequired()])
    target_list_id = StringField('ID Archief', validators=[DataRequired()])
    klaar_archief_submit = SubmitField('Maak link aan')


class SimplicateTrelloCodesForm(FlaskForm):
    simplicate_code = StringField('Simplicate code', validators=[DataRequired()])
    simplicate_id = StringField('Simplicate id', validators=[DataRequired()])
    trello_sjabloon_code = StringField('Trello sjabloon code', validators=[DataRequired()])
    monthly = BooleanField('Maand')
    quarterly = BooleanField('Kwartaal')
    yearly = BooleanField('Jaar')
    jaarwerk = BooleanField('Jaarwerk')
    simplicate_trello_code_submit = SubmitField('Maak link aan')


class ProjectTrelloCodesForm(FlaskForm):
    def __init__(self, ptc=None, **kwargs):
        super().__init__(**kwargs)
        if ptc is not None and request.method == GET or request.method == POST \
                and self.project_trello_codes_submit.name not in request.form:
            self.planning_periodiek_werk_board_id.data = ptc.planning_periodiek_werk_board_id
            self.planning_jaarwerk_board_id.data = ptc.planning_jaarwerk_board_id
            self.nog_te_plannen_board_id.data = ptc.nog_te_plannen_board_id
            self.month_list_id.data = ptc.month_list_id
            self.quarter_list_id.data = ptc.quarter_list_id
            self.year_list_id.data = ptc.year_list_id
            self.afspraken_planning_volgend_jaar_list_id.data = ptc.afspraken_planning_volgend_jaar_list_id
            self.exception_list_id.data = ptc.exception_list_id
            self.periodiek_sjablonen_list_id.data = ptc.periodiek_sjablonen_list_id
            self.jaarwerk_sjablonen_list_id.data = ptc.jaarwerk_sjablonen_list_id

    planning_periodiek_werk_board_id = StringField('ID Planning Periodiek werk', validators=[DataRequired()])
    planning_jaarwerk_board_id = StringField('ID Jaarwerk', validators=[DataRequired()])
    nog_te_plannen_board_id = StringField('ID Nog te plannen', validators=[DataRequired()])
    month_list_id = StringField('ID Maand', validators=[DataRequired()])
    quarter_list_id = StringField('ID Kwartaal', validators=[DataRequired()])
    year_list_id = StringField('ID Jaar', validators=[DataRequired()])
    afspraken_planning_volgend_jaar_list_id = StringField('ID Afspraken planning volgend jaar',
                                                          validators=[DataRequired()])
    exception_list_id = StringField('ID Simplicate automatisering - uitzonderingen', validators=[DataRequired()])
    periodiek_sjablonen_list_id = StringField('ID Sjablonen Planning Periodiek werk', validators=[DataRequired()])
    jaarwerk_sjablonen_list_id = StringField('ID Sjablonen Jaarwerk', validators=[DataRequired()])
    project_trello_codes_submit = SubmitField('Sla wijzigingen op')


class ProjectTrelloCodesCardsForm(FlaskForm):
    def __init__(self, ptc=None, **kwargs):
        super().__init__(**kwargs)
        if ptc is not None and request.method == GET or request.method == POST \
                and self.project_trello_codes_cards_submit.name not in request.form:
            self.periodiek_sjablonen_card_id.data = ptc.periodiek_sjablonen_card_id
            self.jaarwerk_sjablonen_card_id.data = ptc.jaarwerk_sjablonen_card_id

    periodiek_sjablonen_card_id = StringField('ID Sjablonen Planning Periodiek werk', validators=[DataRequired()])
    jaarwerk_sjablonen_card_id = StringField('ID Sjablonen Jaarwerk', validators=[DataRequired()])
    project_trello_codes_cards_submit = SubmitField('Sla wijzigingen op')

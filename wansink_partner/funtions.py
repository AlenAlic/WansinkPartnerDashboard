from flask import json, current_app
from wansink_partner import db
from wansink_partner.models import Authentication, Employees, SimplicateTrelloCodes, ProjectTrelloCards, \
    ProjectTrelloResults, ProjectTrelloResultsCard
from wansink_partner.values import GET, POST, PUT, IB, BILLING_METHOD, TODO_SLUITEN, SIMPLICATE_LIMIT
import requests as http_requests
import time
from datetime import date, timedelta


def trello_request(method=GET, api=tuple(), params=None):
    auth = Authentication.query.first()
    auth = {"key": auth.trello_key, "token": auth.trello_token}
    if params is not None:
        auth.update(params)
    req = http_requests.request(method, f"https://api.trello.com/1/{'/'.join(api)}", params=auth)
    return json.loads(req.text) if req.status_code == 200 else None


def simplicate_request(method=GET, api=tuple(), params=None, delay=False):
    auth = Authentication.query.first()
    headers = {"Authentication-Key": auth.simplicate_key, "Authentication-Secret": auth.simplicate_secret,
               "content-type": "application/json"}
    req = http_requests.request(method, f"https://wansinkpartner.simplicate.nl/api/v2/{'/'.join(api)}",
                                params=params, headers=headers)
    if delay:
        time.sleep(0.5)
    return json.loads(req.text)['data'] if req.status_code == 200 else None


def get_id(resource, name):
    """"Gets id of a Board, List or Card from a resource, given the name. Returns None if no match is found."""
    all_ids = [d['id'] for d in resource if d['name'] == name]
    if len(all_ids) > 0:
        return all_ids[-1]
    return None


def generate_linked_employees():
    trello_members = trello_request(api=("organizations", "wansinkpartner", "members"))
    simplicate_members = simplicate_request(api=("hrm", "employee"))
    trello_names, simplicate_names, overlapping_names, remaining_trello_names, remaining_simplicate_names, \
        added_employees = [], [], [], [], [], []
    if trello_members is not None and simplicate_members is not None:
        trello_members = {t["fullName"]: t for t in trello_members}
        simplicate_members = {s["name"]: s for s in simplicate_members}
        trello_names = sorted([t for t in trello_members])
        simplicate_names = sorted([s for s in simplicate_members])
        overlapping_names = sorted([n for n in simplicate_names if n in trello_names and n in simplicate_names])
        remaining_trello_names = sorted([n for n in trello_names if n not in overlapping_names])
        remaining_simplicate_names = sorted([n for n in simplicate_names if n not in overlapping_names])
        for name in [n for n in overlapping_names if n not in [e.full_name for e in Employees.query.all()]]:
            employee = Employees()
            employee.full_name = name
            employee.trello_id = trello_members[name]["id"]
            employee.simplicate_id = simplicate_members[name]["id"]
            db.session.add(employee)
            added_employees.append(name)
        db.session.commit()
    return added_employees, remaining_trello_names, remaining_simplicate_names


def get_simplicate_projects(future=False):
    projects_dump = []
    if current_app.config.get('DEBUG') and not future:
        for i in range(0, SIMPLICATE_LIMIT * 11, SIMPLICATE_LIMIT):
            projects = simplicate_request(api=("projects", "project"),
                                          params={"offset": i, 'q[name]': 'TEST*', "q[created][ge]": "2019-02-26"})
            projects_dump.extend(projects)
            if len(projects) == 0:
                break
    else:
        if future:
            yesterday = date.today()
            today = date.today() + timedelta(days=1)
        else:
            yesterday = date.today() - timedelta(days=1)
            today = date.today()
        for i in range(0, SIMPLICATE_LIMIT * 11, SIMPLICATE_LIMIT):
            projects = simplicate_request(api=("projects", "project"),
                                          params={"q[created][ge]": yesterday.isoformat(),
                                                  "q[created][le]": today.isoformat(), "offset": i})
            if projects is not None:
                projects_dump.extend(projects)
            else:
                projects = []
            if len(projects) == 0:
                break
    return projects_dump


class SimplicateTrelloCodesContainer:
    def __init__(self):
        self.ptc = ProjectTrelloCards.query.first()
        self.codes = SimplicateTrelloCodes.query.all()
        self.monthly = {c.simplicate_id: c for c in self.codes if c.monthly}
        self.quarterly = {c.simplicate_id: c for c in self.codes if c.quarterly}
        self.yearly = {c.simplicate_id: c for c in self.codes if c.yearly}
        self.jaarwerk = {c.simplicate_id: c for c in self.codes if c.jaarwerk}
        self.monthly_and_quarterly = {c.simplicate_id: c for c in self.codes if c.monthly or c.quarterly}
        self.all_codes = {c.simplicate_id: c for c in self.codes}

    def is_monthly(self, services):
        return not set(get_service_code_ids(services)).isdisjoint(self.monthly)

    def is_quarterly(self, services):
        return not set(get_service_code_ids(services)).isdisjoint(self.quarterly)

    def is_monthly_and_quarterly(self, services):
        return self.is_monthly(services) and self.is_quarterly(services)

    def is_yearly(self, services):
        return not set(get_service_code_ids(services)).isdisjoint(self.yearly)

    def is_jaarwerk(self, services):
        return not set(get_service_code_ids(services)).isdisjoint(self.jaarwerk)

    def is_exception(self, services):
        return set(get_service_code_ids(services)).isdisjoint(self.all_codes)

    @staticmethod
    def filter_services(services, reference):
        return [s for s in services if get_service_code_ids([s])[0] in reference]

    def create_project_cards(self, projects):
        for project in projects:
            result = ProjectTrelloResults()
            result.project_id = project["id"]
            result.name = project['name']
            result.link = project['simplicate_url']
            services = simplicate_request(api=("projects", "service"), params={"q[project_id]": project['id']})
            # if self.is_monthly_and_quarterly(services):
            #     card = create_card(project, self.filter_services(services, self.monthly),
            #                        target_list=self.ptc.month_list_id,
            #                        sjabloon=self.ptc.periodiek_sjablonen_card_id)
            #     if card is not None:
            #         result.cards.append(create_database_card(card, self.ptc.planning_periodiek_werk_board_name,
            #                                                  self.ptc.month_list_name))
            #     card = create_card(project, self.filter_services(services, self.monthly_and_quarterly),
            #                        target_list=self.ptc.quarter_list_id,
            #                        sjabloon=self.ptc.periodiek_sjablonen_card_id)
            #     if card is not None:
            #         result.cards.append(create_database_card(card, self.ptc.planning_periodiek_werk_board_name,
            #                                                  self.ptc.quarter_list_name))
            if self.is_monthly(services):
                card = create_card(project, self.filter_services(services, self.monthly),
                                   target_list=self.ptc.month_list_id,
                                   sjabloon=self.ptc.periodiek_sjablonen_card_id)
                if card is not None:
                    result.cards.append(create_database_card(card, self.ptc.planning_periodiek_werk_board_name,
                                                             self.ptc.month_list_name))
                card = create_card(project, self.filter_services(services, self.monthly),
                                   target_list=self.ptc.quarter_list_id,
                                   sjabloon=self.ptc.periodiek_sjablonen_card_id)
                if card is not None:
                    result.cards.append(create_database_card(card, self.ptc.planning_periodiek_werk_board_name,
                                                             self.ptc.quarter_list_name))
            if self.is_quarterly(services):
                card = create_card(project, self.filter_services(services, self.quarterly),
                                   target_list=self.ptc.quarter_list_id,
                                   sjabloon=self.ptc.periodiek_sjablonen_card_id)
                if card is not None:
                    result.cards.append(create_database_card(card, self.ptc.planning_periodiek_werk_board_name,
                                                             self.ptc.quarter_list_name))
            if self.is_yearly(services):
                card = create_card(project, self.filter_services(services, self.yearly),
                                   target_list=self.ptc.year_list_id,
                                   sjabloon=self.ptc.periodiek_sjablonen_card_id)
                if card is not None:
                    result.cards.append(create_database_card(card, self.ptc.planning_periodiek_werk_board_name,
                                                             self.ptc.year_list_name))
            if self.is_jaarwerk(services):
                card = create_card(project, self.filter_services(services, self.jaarwerk),
                                   target_list=self.ptc.afspraken_planning_volgend_jaar_list_id,
                                   sjabloon=self.ptc.jaarwerk_sjablonen_card_id, change_name=True, sluiten=True)
                # Move card to exceptions only if all services are of the type IB
                if card is not None:
                    if all(s['name'].startswith(IB) for s in services):
                        trello_request(method=PUT, api=("cards", card["id"]),
                                       params={"idList": self.ptc.exception_list_id})
                        result.cards.append(create_database_card(card, self.ptc.nog_te_plannen_board_name,
                                                                 self.ptc.exception_list_name))
                    else:
                        result.cards.append(create_database_card(card, self.ptc.planning_jaarwerk_board_name,
                                                                 self.ptc.afspraken_planning_volgend_jaar_list_name))
            if self.is_exception(services):
                card = create_card(project, services, target_list=self.ptc.exception_list_id,
                                   change_name=True, exception=True)
                if card is not None:
                    result.cards.append(create_database_card(card, self.ptc.nog_te_plannen_board_name,
                                                             self.ptc.exception_list_name))
            db.session.add(result)
            db.session.commit()


def create_card(project, services, target_list=None, sjabloon=None, exception=False, change_name=False, sluiten=False):
    # Name Trello Card, depending on if the Simplicate Project is for a organization or a person
    if 'organization' in project:
        card_name_target = project['organization']['name']
    elif 'person' in project:
        card_name_target = project['person']['full_name']
    else:
        card_name_target = ''

    # Change card name. This is only for cards that go to the Board "Planning Jaarwerk" or the Board "Nog te plannen"
    if change_name:
        card_name_target += f" - {project['name']}"

    # Project manager from Simplicate to add to Card
    manager = project['project_manager']['id'] if 'project_manager' in project else ""
    employee = Employees.query.filter(Employees.simplicate_id == manager).first()
    if employee is not None:
        manager = employee.trello_id

    # Create card
    params = {"name": card_name_target, "desc": create_description(project), "idList": target_list}
    if manager != "":
        params.update({"idMembers": manager})
    card = trello_request(method=POST, api=("cards",), params=params)

    if not exception:
        if len(services) > 0:
            service_code_ids = get_service_code_ids(services)
            checklists = trello_request(api=("cards", sjabloon, "checklists"),
                                        params={"checkItems": "all", "checkItem_fields": "all", "fields": "all"})
            checklists_to_add = {c.trello_code: None for c in SimplicateTrelloCodes.query.all()
                                 if c.simplicate_id in service_code_ids}
            if sluiten:
                checklists_to_add.update({TODO_SLUITEN: None})
            for c in checklists:
                if c["name"] in checklists_to_add:
                    checklists_to_add[c["name"]] = c["id"]
            for checklist in checklists_to_add:
                trello_request(method=POST, api=("cards", card["id"], "checklists"),
                               params={"idChecklistSource": checklists_to_add[checklist]})
    return card


def get_service_code_ids(services):
    return [service['default_service_id'] for service in services]


def create_description(project):
    desc = 'SIM\n\n'
    desc += 'Link naar project:\n' + project['simplicate_url']
    if project['billable']:
        desc += '\n\n' + 'Factuurmethode:\n' + BILLING_METHOD[project['hours_rate_type']]
    if 'note' in project:
        desc += '\n\n' + 'Notities:\n' + project['note']
    return desc


def create_database_card(card, board_name, list_name):
    result_card = ProjectTrelloResultsCard()
    result_card.card_id = card["id"]
    result_card.card_name = card["name"]
    result_card.card_desc = card["desc"]
    result_card.card_link = card["shortUrl"]
    result_card.board_id = card["idBoard"]
    result_card.board_name = board_name
    result_card.list_id = card["idList"]
    result_card.list_name = list_name
    return result_card

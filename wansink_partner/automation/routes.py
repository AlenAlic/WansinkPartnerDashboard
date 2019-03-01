from flask import render_template, request, redirect, url_for, flash, Markup, Response
from flask_login import login_required, login_user, logout_user
from wansink_partner.automation import bp
from wansink_partner.automation.forms import GenerateEmployeeLinksForm, EmployeeForm, JaarwerkForm, MaandwerkForm, \
    KlaarArchiefLinkForm, SimplicateTrelloCodesForm, ProjectTrelloCodesForm, ProjectTrelloCodesCardsForm, SwitchUserForm
from wansink_partner.models import User, auth_required, Jaarwerk, JaarwerkResult, Maandwerk, MaandwerkCopyResult, \
    MaandwerkMoveResult, KlaarArchiefLinks, KlaarArchiefResult
from wansink_partner.values import *
from datetime import datetime as dt
from wansink_partner.funtions import *


@bp.route('/tests', methods=[GET, POST])
@login_required
def tests():
    if request.method == POST:
        if "test_jaarwerk" in request.form:
            http_requests.request(GET, f"{request.host_url}automation/run_jaarwerk",
                                  params={"Auth-Key": current_app.config.get('AUTH_KEY'), "Override": True})
        if "test_maandwerk" in request.form:
            http_requests.request(GET, f"{request.host_url}automation/run_maandwerk_copy",
                                  params={"Auth-Key": current_app.config.get('AUTH_KEY'), "Override": True})
            http_requests.request(GET, f"{request.host_url}automation/run_maandwerk_move",
                                  params={"Auth-Key": current_app.config.get('AUTH_KEY'), "Override": True})
        if "test_klaar_archief" in request.form:
            http_requests.request(GET, f"{request.host_url}automation/run_klaar_archief",
                                  params={"Auth-Key": current_app.config.get('AUTH_KEY'), "Override": True})
        if "test_project_trello_cards" in request.form:
            http_requests.request(GET, f"{request.host_url}automation/run_project_trello_cards",
                                  params={"Auth-Key": current_app.config.get('AUTH_KEY'), "Override": True})
    return render_template('automation/tests.html')


@bp.route('/accounts', methods=[GET, POST])
@login_required
def accounts():
    form = SwitchUserForm()
    users = User.query.filter(User.is_active.is_(True), User.access != ACCESS[ADMIN]).order_by(User.username).all()
    form.user.choices = map(lambda user_map: (user_map.user_id, user_map.username), users)
    if request.method == POST:
        if form.submit.name in request.form and form.validate_on_submit():
            user = User.query.filter(User.user_id == form.user.data).first()
            if user is not None:
                logout_user()
                login_user(user)
            else:
                flash('User account is not active.')
            return redirect(url_for('main.index'))
    return render_template('automation/accounts.html', form=form)


@bp.route('/dashboard', methods=[GET])
@login_required
def dashboard():
    jaarwerk_result = JaarwerkResult.query.order_by(JaarwerkResult.archive_id.desc()).first()
    jaarwerk_result_summary = None
    if jaarwerk_result is not None:
        jaarwerk_result_summary = jaarwerk_result.result.split("\r\n\r\n")[0]
    mw = Maandwerk.query.first()
    maandwerk_move_result = MaandwerkMoveResult.query.order_by(MaandwerkMoveResult.archive_id.desc()).first()
    maandwerk_move_result_summary = None
    if maandwerk_move_result is not None:
        maandwerk_move_result_summary = maandwerk_move_result.result.split("\r\n\r\n")[0]
    maandwerk_copy_result = MaandwerkCopyResult.query.order_by(MaandwerkCopyResult.archive_id.desc()).first()
    maandwerk_copy_result_summary = None
    if maandwerk_copy_result is not None:
        maandwerk_copy_result_summary = maandwerk_copy_result.result.split("\r\n\r\n")[0]
    links = KlaarArchiefLinks.query.all()
    klaar_archief_results = KlaarArchiefResult.query.order_by(KlaarArchiefResult.archive_id.desc())\
        .limit(len(links)).all()[:len(links)]
    klaar_archief_summaries = []
    if len(klaar_archief_results) == len(links) and len(links) != 0:
        klaar_archief_summaries = [r.result.split("\r\n\r\n")[0] for r in klaar_archief_results]
    cutoff_datetime = dt.utcnow() - timedelta(days=1)
    project_trello_cards_results = ProjectTrelloResults.query.filter(ProjectTrelloResults.timestamp > cutoff_datetime)\
        .order_by(ProjectTrelloResults.archive_id).all()
    projects_tomorrow = get_simplicate_projects(future=True)
    return render_template('automation/dashboard.html', now=dt.utcnow(),
                           jaarwerk_result=jaarwerk_result, jaarwerk_result_summary=jaarwerk_result_summary,
                           mw=mw, maandwerk_move_result=maandwerk_move_result,
                           maandwerk_move_result_summary=maandwerk_move_result_summary,
                           maandwerk_copy_result=maandwerk_copy_result,
                           maandwerk_copy_result_summary=maandwerk_copy_result_summary,
                           klaar_archief_results=klaar_archief_results,
                           klaar_archief_summaries=klaar_archief_summaries,
                           project_trello_cards_results=project_trello_cards_results,
                           projects_tomorrow=projects_tomorrow)


@bp.route('/override_run_jaarwerk', methods=['GET', 'POST'])
@login_required
def override_run_jaarwerk():
    http_requests.request(GET, f"{request.host_url}automation/run_jaarwerk",
                          params={"Auth-Key": current_app.config.get('AUTH_KEY'), "Override": True})
    return redirect(url_for('automation.manual_override'))


@bp.route('/override_run_maandwerk_copy', methods=['GET', 'POST'])
@login_required
def override_run_maandwerk_copy():
    http_requests.request(GET, f"{request.host_url}automation/run_maandwerk_copy",
                          params={"Auth-Key": current_app.config.get('AUTH_KEY'), "Override": True})
    return redirect(url_for('automation.manual_override'))


@bp.route('/override_run_maandwerk_move', methods=['GET', 'POST'])
@login_required
def override_run_maandwerk_move():
    http_requests.request(GET, f"{request.host_url}automation/run_maandwerk_move",
                          params={"Auth-Key": current_app.config.get('AUTH_KEY'), "Override": True})
    return redirect(url_for('automation.manual_override'))


@bp.route('/override_run_klaar_archief', methods=['GET', 'POST'])
@login_required
def override_run_klaar_archief():
    http_requests.request(GET, f"{request.host_url}automation/run_klaar_archief",
                          params={"Auth-Key": current_app.config.get('AUTH_KEY'), "Override": True})
    return redirect(url_for('automation.manual_override'))


@bp.route('/override_run_project_trello_cards', methods=['GET', 'POST'])
@login_required
def override_run_project_trello_cards():
    http_requests.request(GET, f"{request.host_url}automation/run_project_trello_cards",
                          params={"Auth-Key": current_app.config.get('AUTH_KEY'), "Override": True})
    return redirect(url_for('automation.manual_override'))


@bp.route('/trello', methods=['GET', 'POST'])
@login_required
def trello():
    boards = trello_request(api=("organization", "wansinkpartner", "boards"), params={"lists": "open"})
    return render_template('automation/trello.html', boards=boards)


@bp.route('/jaarwerk', methods=['GET', 'POST'])
@login_required
def jaarwerk():
    jw = Jaarwerk.query.first()
    form = JaarwerkForm(jw)
    if request.method == POST:
        if form.jaarwerk_submit.name in request.form and form.validate_on_submit():
            source_board = trello_request(api=("boards", form.source_board_id.data))
            target_board = trello_request(api=("boards", form.target_board_id.data))
            target_list = trello_request(api=("lists", form.target_list_id.data))
            if source_board is not None and target_board is not None and target_list is not None:
                if Jaarwerk.query.first() is None:
                    jw = Jaarwerk()
                jw.source_board_id = source_board["id"]
                jw.source_board_name = source_board["name"]
                jw.target_board_id = target_board["id"]
                jw.target_board_name = target_board["name"]
                jw.target_list_id = target_list["id"]
                jw.target_list_name = target_list["name"]
                db.session.add(jw)
                db.session.commit()
                flash("Wijzigingen zijn opgeslagen")
                return redirect(url_for('automation.jaarwerk'))
            else:
                if source_board is None and target_board is None and target_list is None:
                    flash("Kon geen data van Trello binnenhalen! Probeer het later nog eens", "danger")
                else:
                    if source_board is None:
                        form.source_board_id.errors.append(BOARD_NOT_FOUND)
                    if target_board is None:
                        form.target_board_id.errors.append(BOARD_NOT_FOUND)
                    if target_list is None:
                        form.target_list_id.errors.append(LIST_NOT_FOUND)
                    flash("Niet alle id's konden worden geverifieerd. Wijzigingen zijn niet opgeslagen.")
    lists = []
    source_lists = None
    if jw.source_board_id is not None:
        source_lists = trello_request(api=("boards", jw.source_board_id), params={"lists": "open"})
        if source_lists is not None:
            check_lists = [f"{m} {y}" for y in range(dt.now().year, dt.now().year + 3) for m in MONTHS_DICT.values()]
            lists = source_lists["lists"]
            # lists = sorted([l for l in lists if l["name"] in check_lists],
            #                key=lambda x: MONTHS_SORT_DICT[x["name"].split(" ")[0]])
            lists = [l for l in lists if l["name"] in check_lists]
    return render_template('automation/jaarwerk.html', form=form, jw=jw, source_lists=source_lists, lists=lists)


@bp.route('/run_jaarwerk', methods=['GET'])
@auth_required
def run_jaarwerk():
    if date.today().day == 1 or current_app.config.get('DEBUG') \
            or request.args.get("Override", default=False, type=bool):
        jw = Jaarwerk.query.first()
        list_name_source = f"{MONTHS_DICT[dt.utcnow().month]} {str(dt.utcnow().year)}"
        lists = trello_request(api=("boards", jw.source_board_id, "lists"))
        errors = True
        if lists is not None:
            list_id_source = get_id(lists, list_name_source)
            if list_id_source is not None:
                cards = trello_request(api=("lists", list_id_source, "cards"))
                trello_request(method=POST, api=("lists", list_id_source, "moveAllCards"),
                               params={"idBoard": jw.target_board_id, "idList": jw.target_list_id})
                if len(cards) > 0:
                    text = f"Jaarwerk automatisering succesvol.\r\n\r\n" + \
                           f"De volgende kaarten zijn verplaatst:\r\n" + \
                           "\r\n".join([card["name"] for card in cards])
                else:
                    text = "Er waren geen kaarten aanwezig om te verplaatsen."
                trello_request(method=PUT, api=("lists", list_id_source), params={"closed": "true"})
                errors = False
            else:
                text = f"Fout tijdens het ophalen van de lijst van het bord {jw.source_board_name}.\r\n" \
                    f"Lijst met de naam {list_name_source} niet gevonden."
        else:
            text = f"Fout tijdens het ophalen van het bord {jw.source_board_name}."
        result = JaarwerkResult()
        result.result = text
        db.session.add(result)
        db.session.commit()
        if errors:
            return Response(status=500)
        return Response(status=200)


@bp.route('/maandwerk', methods=['GET', 'POST'])
@login_required
def maandwerk():
    mw = Maandwerk.query.first()
    form = MaandwerkForm(mw)
    if request.method == POST:
        if form.maandwerk_submit.name in request.form and form.validate_on_submit():
            source_board = trello_request(api=("boards", form.source_board_id.data))
            source_list_month = trello_request(api=("lists", form.source_list_month_id.data))
            source_list_quarter = trello_request(api=("lists", form.source_list_quarter_id.data))
            target_board = trello_request(api=("boards", form.target_board_id.data))
            source_list = trello_request(api=("lists", form.source_list_id.data))
            target_list = trello_request(api=("lists", form.target_list_id.data))
            if source_board is not None and source_list_month is not None and source_list_quarter is not None \
                    and target_board is not None and source_list is not None and target_list is not None:
                if Maandwerk.query.first() is None:
                    mw = Maandwerk()
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
                db.session.add(mw)
                db.session.commit()
                flash("Wijzigingen zijn opgeslagen")
                return redirect(url_for('automation.maandwerk'))
            else:
                if source_board is None and source_list_month is None and source_list_quarter is None \
                        and target_board is None and source_list is None and target_list is None:
                    flash("Kon geen data van Trello binnenhalen! Probeer het later nog eens", "danger")
                else:
                    if source_board is None:
                        form.source_list_id.source_board_id.append(BOARD_NOT_FOUND)
                    if source_list_month is None:
                        form.source_list_month_id.errors.append(LIST_NOT_FOUND)
                    if source_list_quarter is None:
                        form.source_list_quarter_id.errors.append(LIST_NOT_FOUND)
                    if target_board is None:
                        form.target_board_id.errors.append(BOARD_NOT_FOUND)
                    if source_list is None:
                        form.source_list_id.errors.append(LIST_NOT_FOUND)
                    if target_list is None:
                        form.target_list_id.errors.append(LIST_NOT_FOUND)
                    flash("Niet alle id's konden worden geverifieerd. Wijzigingen zijn niet opgeslagen.")
    return render_template('automation/maandwerk.html', form=form, mw=mw)


@bp.route('/run_maandwerk_copy', methods=['GET'])
@auth_required
def run_maandwerk_copy():
    if date.today().day == 1 or current_app.config.get('DEBUG') \
            or request.args.get("Override", default=False, type=bool):
        mw = Maandwerk.query.first()
        now = dt.now()
        source_list_id = mw.source_list_quarter_id if (now.month - 1) % 3 == 0 else mw.source_list_month_id
        source_list_name = mw.source_list_quarter_name if (now.month - 1) % 3 == 0 else mw.source_list_month_name
        new_list = trello_request(method=POST, api=("lists",),
                                  params={"name": source_list_name, "idBoard": mw.target_board_id,
                                          "idListSource": source_list_id})
        errors = True
        if new_list is not None:
            cards_copy = trello_request(api=("lists", new_list["id"], "cards"))
            for card in cards_copy:
                trello_request(method=PUT, api=("cards", card['id']),
                               params={"name": f"{MONTH_ABBREVIATION_DICT[now.month - 1]} - {card['name']}"})
            trello_request(method=POST, api=("lists", new_list["id"], "moveAllCards"),
                           params={"idBoard": mw.target_board_id, "idList": mw.target_list_id})
            if len(cards_copy) > 0:
                text = f"Kopiëren van de lijst {source_list_name} succesvol.\r\n\r\n" + \
                       f"De volgende kaarten zijn gekopieerd:\r\n" + \
                       f"\r\n".join([card["name"] for card in cards_copy])
            else:
                text = f"Er waren geen kaarten aanwezig om te kopiëren van de lijst {source_list_name}."
            trello_request(method=PUT, api=("lists", new_list["id"]), params={"closed": "true"})
            errors = False
        else:
            text = f"Fout tijdens het ophalen van de lijst {source_list_name}. Lijst niet gevonden."
        result = MaandwerkCopyResult()
        result.result = text
        db.session.add(result)
        db.session.commit()
        if errors:
            return Response(status=500)
        return Response(status=200)


@bp.route('/run_maandwerk_move', methods=['GET'])
@auth_required
def run_maandwerk_move():
    if date.today().day == 1 or current_app.config.get('DEBUG') \
            or request.args.get("Override", default=False, type=bool):
        mw = Maandwerk.query.first()
        now = dt.now()
        cards_move = trello_request(api=("lists", mw.source_list_id, "cards"))
        for card in cards_move:
            trello_request(method=PUT, api=("cards", card['id']),
                           params={"name": f"{MONTH_ABBREVIATION_DICT[now.month - 1]} - {card['name']}"})
        trello_request(method=POST, api=("lists", mw.source_list_id, "moveAllCards"),
                       params={"idBoard": mw.target_board_id, "idList": mw.target_list_id})
        if len(cards_move) > 0:
            text = f"Verplaatsen kaarten van de lijst {mw.source_list_name} succesvol.\r\n\r\n" + \
                   f"De volgende kaarten zijn verplaatst: \r\n" + \
                   f"\r\n".join([card["name"] for card in cards_move])
        else:
            text = f"Er waren geen kaarten aanwezig om te kopiëren van de lijst {mw.source_list_name}."
        result = MaandwerkMoveResult()
        result.result = text
        db.session.add(result)
        db.session.commit()
        return Response(status=200)


@bp.route('/klaar_archief', methods=['GET', 'POST'])
@login_required
def klaar_archief():
    form = KlaarArchiefLinkForm()
    if request.method == POST:
        if form.klaar_archief_submit.name in request.form and form.validate_on_submit():
            source_list = trello_request(api=("lists", form.source_list_id.data))
            target_list = trello_request(api=("lists", form.target_list_id.data))
            if source_list is not None and target_list is not None:
                board = trello_request(api=("boards", target_list["idBoard"]))
                link = KlaarArchiefLinks()
                link.source_id = source_list["id"]
                link.source_name = source_list["name"]
                link.target_id = target_list["id"]
                link.target_name = target_list["name"]
                link.board_id = board["id"]
                link.board_name = board["name"]
                db.session.add(link)
                db.session.commit()
                flash(f"Link {link.name} aangemaakt.")
                return redirect(url_for('automation.klaar_archief'))
            else:
                if source_list is None and target_list is None:
                    flash("Kon geen data van Trello binnenhalen! Probeer het later nog eens", "danger")
                else:
                    if source_list is None:
                        form.source_list_id.errors.append(LIST_NOT_FOUND)
                    if target_list is None:
                        form.target_list_id.errors.append(LIST_NOT_FOUND)
                    flash("Niet alle id's konden worden geverifieerd. Wijzigingen zijn niet opgeslagen.")
    links = KlaarArchiefLinks.query.all()
    return render_template('automation/klaar_archief.html', form=form, links=links)


@bp.route('/delete_klaar_archief_link/<int:link_id>', methods=[GET])
@login_required
def delete_klaar_archief_link(link_id):
    link = KlaarArchiefLinks.query.get(link_id)
    if link is not None:
        flash(f"{link} verwijderd.")
        db.session.delete(link)
        db.session.commit()
    else:
        flash(f"Link niet gevonden in database")
    return redirect(url_for('automation.klaar_archief'))


@bp.route('/run_klaar_archief', methods=['GET'])
@auth_required
def run_klaar_archief():
    if date.today().day == 1 or current_app.config.get('DEBUG') \
            or request.args.get("Override", default=False, type=bool):
        for link in KlaarArchiefLinks.query.all():
            cards = trello_request(api=("lists", link.source_id, "cards"))
            trello_request(method=POST, api=("lists", link.source_id, "moveAllCards"),
                           params={"idBoard": link.board_id, "idList": link.target_id})
            if len(cards) > 0:
                text = f"Klaar archief automatisering succesvol uitgevoerd.\r\n\r\n" + \
                       f"De volgende kaarten zijn verplaatst: \r\n" + \
                       "\r\n".join([card["name"] for card in cards])
            else:
                text = "Er waren geen kaarten aanwezig om te verplaatsen."
            result = KlaarArchiefResult()
            result.name = link.board_name
            result.result = text
            db.session.add(result)
            db.session.commit()
        return Response(status=200)


@bp.route('/simplicate', methods=['GET', 'POST'])
@login_required
def simplicate():
    form = SimplicateTrelloCodesForm()
    if request.method == "POST":
        if form.simplicate_trello_code_submit.name in request.form and form.validate_on_submit():
            link = SimplicateTrelloCodes()
            link.simplicate_code = form.simplicate_code.data
            link.trello_code = form.trello_sjabloon_code.data
            link.monthly = form.monthly.data
            link.quarterly = form.quarterly.data
            link.yearly = form.yearly.data
            link.jaarwerk = form.jaarwerk.data
            db.session.add(link)
            db.session.commit()
            flash(f"Link aangemaakt tussen Simplicate en Trello codes {link.simplicate_code} en {link.trello_code}.")
            return redirect(url_for('automation.simplicate'))
    codes = SimplicateTrelloCodes.query.order_by(SimplicateTrelloCodes.code_id).all()
    live_codes = simplicate_request(api=("services", "defaultservice"))
    return render_template('automation/simplicate.html', form=form, codes=codes, live_codes=live_codes)


@bp.route('/delete_simplicate_trello_link/<int:code_id>', methods=[GET])
@login_required
def delete_simplicate_trello_link(code_id):
    code = SimplicateTrelloCodes.query.get(code_id)
    if code is not None:
        flash(f"Link voor {code} verwijderd.")
        db.session.delete(code)
        db.session.commit()
    else:
        flash(f"Link niet gevonden in database.")
    return redirect(url_for('automation.simplicate'))


@bp.route('/medewerker_links', methods=[GET, POST])
@login_required
def medewerker_links():
    form = EmployeeForm()
    generate_form = GenerateEmployeeLinksForm()
    if request.method == POST:
        if form.employee_submit.name in request.form and form.validate_on_submit():
            trello_employee = trello_request(api=("members", form.trello_id.data))
            simplicate_employee = simplicate_request(api=("hrm", "employee", form.simplicate_id.data))
            if trello_employee is not None and simplicate_employee is not None:
                employee = Employees()
                employee.full_name = form.full_name.data
                employee.trello_id = form.trello_id.data
                employee.simplicate_id = form.simplicate_id.data
                db.session.add(employee)
                db.session.commit()
                flash(f"Link aangemaakt tussen Trello en Simplicate voor {form.full_name.data}.")
                return redirect(url_for('automation.medewerker_links'))
            else:
                if trello_request(api=("organizations", "wansinkpartner")) is None:
                    flash("Kon geen data van Trello binnenhalen! Probeer het later nog eens", "danger")
                if trello_employee is None:
                    form.trello_id.errors.append(EMPLOYEE_NOT_FOUND)
                if simplicate_request(api=("hrm", "employee")) is None:
                    flash("Kon geen data van Simplicate binnenhalen! Probeer het later nog eens", "danger")
                if simplicate_employee is None:
                    form.simplicate_id.errors.append(EMPLOYEE_NOT_FOUND)
                flash("Niet alle id's konden worden geverifieerd. Wijzigingen zijn niet opgeslagen.")
        if generate_form.generate_employee_links_submit.name in request.form and generate_form.validate_on_submit():
            added_employees, remaining_trello_names, remaining_simplicate_names = generate_linked_employees()
            flash(Markup(f"Links tussen Trello en Simplicate zijn aangemaakt voor de volgende personen:"
                         f"<br/><br/>{'<br/>'.join(added_employees)}."))
            return redirect(url_for('automation.medewerker_links'))
    employees = Employees.query.order_by(Employees.full_name).all()
    employee_ids = [e.trello_id for e in employees] + [e.simplicate_id for e in employees]
    trello_members = trello_request(api=("organizations", "wansinkpartner", "members"))
    trello_members = sorted([m for m in trello_members if m["id"] not in employee_ids],
                            key=lambda x: x["fullName"])
    simplicate_members = simplicate_request(api=("hrm", "employee"))
    simplicate_members = sorted([m for m in simplicate_members if m["id"] not in employee_ids],
                                key=lambda x: x["name"])
    return render_template('automation/medewerker_links.html', form=form, generate_form=generate_form,
                           employees=employees, trello_members=trello_members, simplicate_members=simplicate_members)


@bp.route('/delete_employee/<int:employee_id>', methods=[GET])
@login_required
def delete_employee(employee_id):
    employee = Employees.query.get(employee_id)
    if employee is not None:
        flash(f"Link voor {employee} verwijderd.")
        db.session.delete(employee)
        db.session.commit()
    else:
        flash(f"Link niet gevonden in database.")
    return redirect(url_for('automation.medewerker_links'))


@bp.route('/project_trello_cards', methods=['GET', 'POST'])
@login_required
def project_trello_cards():
    ptc = ProjectTrelloCards.query.first()
    form = ProjectTrelloCodesForm(ptc)
    sjabloon_form = ProjectTrelloCodesCardsForm(ptc)
    if request.method == POST:
        if form.project_trello_codes_submit.name in request.form and form.validate_on_submit():
            planning_periodiek_werk_board = trello_request(api=("boards", form.planning_periodiek_werk_board_id.data))
            planning_jaarwerk_board = trello_request(api=("boards", form.planning_jaarwerk_board_id.data))
            nog_te_plannen_board = trello_request(api=("boards", form.nog_te_plannen_board_id.data))
            month_list = trello_request(api=("lists", form.month_list_id.data))
            quarter_list = trello_request(api=("lists", form.quarter_list_id.data))
            year_list = trello_request(api=("lists", form.year_list_id.data))
            afspraken_planning_volgend_jaar_list = \
                trello_request(api=("lists", form.afspraken_planning_volgend_jaar_list_id.data))
            exception_list = trello_request(api=("lists", form.exception_list_id.data))
            periodiek_sjablonen_list = trello_request(api=("lists", form.periodiek_sjablonen_list_id.data))
            jaarwerk_sjablonen_list = trello_request(api=("lists", form.jaarwerk_sjablonen_list_id.data))
            if planning_periodiek_werk_board is not None and planning_jaarwerk_board is not None \
                    and nog_te_plannen_board is not None and month_list is not None \
                    and quarter_list is not None and year_list is not None \
                    and afspraken_planning_volgend_jaar_list is not None and exception_list is not None \
                    and periodiek_sjablonen_list is not None and jaarwerk_sjablonen_list is not None:
                if ProjectTrelloCards.query.first() is None:
                    ptc = ProjectTrelloCards()
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
                db.session.add(ptc)
                db.session.commit()
                flash("Wijzigingen zijn opgeslagen")
                return redirect(url_for('automation.project_trello_cards'))
            else:
                if trello_request(api=("organizations", "wansinkpartner")) is None:
                    flash("Kon geen data van Trello binnenhalen! Probeer het later nog eens", "danger")
                else:
                    if planning_periodiek_werk_board is None:
                        form.planning_periodiek_werk_board_id.errors.append(BOARD_NOT_FOUND)
                    if planning_jaarwerk_board is None:
                        form.planning_jaarwerk_board_id.errors.append(BOARD_NOT_FOUND)
                    if nog_te_plannen_board is None:
                        form.nog_te_plannen_board_id.errors.append(BOARD_NOT_FOUND)
                    if month_list is None:
                        form.month_list_id.errors.append(LIST_NOT_FOUND)
                    if quarter_list is None:
                        form.quarter_list_id.errors.append(LIST_NOT_FOUND)
                    if year_list is None:
                        form.year_list_id.errors.append(LIST_NOT_FOUND)
                    if afspraken_planning_volgend_jaar_list is None:
                        form.afspraken_planning_volgend_jaar_list_id.errors.append(LIST_NOT_FOUND)
                    if exception_list is None:
                        form.exception_list_id.errors.append(LIST_NOT_FOUND)
                    if periodiek_sjablonen_list is None:
                        form.periodiek_sjablonen_list_id.errors.append(LIST_NOT_FOUND)
                    if jaarwerk_sjablonen_list is None:
                        form.jaarwerk_sjablonen_list_id.errors.append(LIST_NOT_FOUND)
                    flash("Niet alle id's konden worden geverifieerd. Wijzigingen zijn niet opgeslagen.")
        if sjabloon_form.project_trello_codes_cards_submit.name in request.form and sjabloon_form.validate_on_submit():
            periodiek_sjablonen_card = trello_request(api=("cards", sjabloon_form.periodiek_sjablonen_card_id.data))
            jaarwerk_sjablonen_card = trello_request(api=("cards", sjabloon_form.jaarwerk_sjablonen_card_id.data))
            if periodiek_sjablonen_card is not None and jaarwerk_sjablonen_card is not None:
                ptc.periodiek_sjablonen_card_id = periodiek_sjablonen_card["id"]
                ptc.periodiek_sjablonen_card_name = periodiek_sjablonen_card["name"]
                ptc.jaarwerk_sjablonen_card_id = jaarwerk_sjablonen_card["id"]
                ptc.jaarwerk_sjablonen_card_name = jaarwerk_sjablonen_card["name"]
                db.session.add(ptc)
                db.session.commit()
                flash("Wijzigingen zijn opgeslagen")
                return redirect(url_for('automation.project_trello_cards'))
            else:
                if trello_request(api=("organizations", "wansinkpartner")) is None:
                    flash("Kon geen data van Trello binnenhalen! Probeer het later nog eens", "danger")
                else:
                    if periodiek_sjablonen_card is None:
                        sjabloon_form.periodiek_sjablonen_card_id.errors.append(CARD_NOT_FOUND)
                    if jaarwerk_sjablonen_card is None:
                        sjabloon_form.jaarwerk_sjablonen_card_id.errors.append(CARD_NOT_FOUND)
                    flash("Niet alle id's konden worden geverifieerd. Wijzigingen zijn niet opgeslagen.")
    periodiek_sjablonen_cards, jaarwerk_sjablonen_cards = None, None
    if ptc.periodiek_sjablonen_list_id is not None and ptc.jaarwerk_sjablonen_list_id is not None:
        periodiek_sjablonen_cards = trello_request(api=("lists", ptc.periodiek_sjablonen_list_id, "cards"))
        jaarwerk_sjablonen_cards = trello_request(api=("lists", ptc.jaarwerk_sjablonen_list_id, "cards"))
    return render_template('automation/project_trello_cards.html', form=form, sjabloon_form=sjabloon_form, ptc=ptc,
                           periodiek_sjablonen_cards=periodiek_sjablonen_cards,
                           jaarwerk_sjablonen_cards=jaarwerk_sjablonen_cards)


@bp.route('/run_project_trello_cards', methods=['GET'])
@auth_required
def run_project_trello_cards():
    if request.args.get("Override", default=False, type=bool):
        projects = get_simplicate_projects()
        container = SimplicateTrelloCodesContainer()
        container.create_project_cards(projects)
        return Response(status=200)


@bp.route('/manual_override', methods=['GET'])
@login_required
def manual_override():
    projects = simplicate_request(api=("projects", "project"),
                                  params={"q[created_at][ge]": current_app.config.get('STARTING_DATE'),
                                          "sort": "-created_at", "limit": SIMPLICATE_LIMIT})
    projects_ids = [p["id"] for p in projects]
    database_projects = ProjectTrelloResults.query\
        .filter(ProjectTrelloResults.project_id.in_([p["id"] for p in projects])).all()
    database_projects_ids = [d.project_id for d in database_projects]
    projects_not_in_database_ids = [p for p in projects_ids if p not in database_projects_ids]
    return render_template('automation/manual_override.html', projects=projects,
                           projects_not_in_database_ids=projects_not_in_database_ids)


@bp.route('/manual_project_trello_cards/<string:project_id>', methods=['GET'])
@login_required
def manual_project_trello_cards(project_id):
    project = simplicate_request(api=("projects", "project"), params={"q[id]": project_id})
    if project is not None:
        container = SimplicateTrelloCodesContainer()
        container.create_project_cards(project)
        flash(f"Kaart(en) aangemaakt voor project {project[0]['name']}.")
    else:
        flash(f"Kon project niet vinden.")
    return redirect(url_for('automation.manual_override'))

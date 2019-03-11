# ACCESS
ADMIN = 'admin'
USER = 'user'
ACCESS = {
    ADMIN: 0,
    USER: 10,
}

# HTTP Methods
GET, POST, PUT = "GET", "POST", "PUT"

# Simplicate limit
SIMPLICATE_LIMIT = 100

# Month number to name dictionary
MONTHS_DICT = {1: "Januari", 2: "Februari", 3: "Maart", 4: "April", 5: "Mei", 6: "Juni",
               7: "Juli", 8: "Augustus", 9: "September", 10: "Oktober", 11: "November", 12: "December"}
MONTHS_SORT_DICT = {MONTHS_DICT[m]: m for m in MONTHS_DICT}
# Month number to name dictionary
MONTH_ABBREVIATION_DICT = {0: "DEC",
                           1: "JAN", 2: "FEB", 3: "MAA", 4: "APR", 5: "MEI", 6: "JUN",
                           7: "JUL", 8: "AUG", 9: "SEP", 10: "OKT", 11: "NOV", 12: "DEC"}

# Misc.
BILLING_METHOD = {'employee_tariff': 'Medewerker uurtarief', 'itemtype_tariff': ' Urensoort uurtarief'}
TODO_SLUITEN = 'TODO sluiten'
BOARD_NOT_FOUND = "Kon bord met dit id niet vinden."
LIST_NOT_FOUND = "Kon lijst met dit id niet vinden."
CARD_NOT_FOUND = "Kon kaart met dit id niet vinden."
EMPLOYEE_NOT_FOUND = "Kon medewerker met dit id niet vinden"

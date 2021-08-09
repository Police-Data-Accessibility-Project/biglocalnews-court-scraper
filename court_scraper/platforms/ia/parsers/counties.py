LOOKUP_BY_ID = {
    "05011": "ADAIR",
    "05021": "ADAMS",
    "01031": "ALLAMAKEE",
    "08041": "APPANOOSE",
    "04051": "AUDUBON",
    "06061": "BENTON",
    "01071": "BLACK HAWK",
    "02081": "BOONE",
    "02091": "BREMER",
    "01101": "BUCHANAN",
    "03111": "BUENA VISTA",
    "02121": "BUTLER",
    "02131": "CALHOUN",
    "02141": "CARROLL",
    "04151": "CASS",
    "07161": "CEDAR",
    "02171": "CERRO GORDO",
    "03181": "CHEROKEE",
    "01191": "CHICKASAW",
    "05201": "CLARKE",
    "03211": "CLAY",
    "01221": "CLAYTON",
    "07231": "CLINTON",
    "03241": "CRAWFORD",
    "05251": "DALLAS",
    "08261": "DAVIS",
    "05271": "DECATUR",
    "01281": "DELAWARE",
    "08291": "DES MOINES",
    "03301": "DICKINSON",
    "01311": "DUBUQUE",
    "03321": "EMMET",
    "01331": "FAYETTE",
    "02341": "FLOYD",
    "02351": "FRANKLIN",
    "04361": "FREMONT",
    "02371": "GREENE",
    "01381": "GRUNDY",
    "05391": "GUTHRIE",
    "02401": "HAMILTON",
    "02411": "HANCOCK",
    "02421": "HARDIN",
    "04431": "HARRISON",
    "08441": "HENRY",
    "01451": "HOWARD",
    "02461": "HUMBOLDT",
    "03471": "IDA",
    "06481": "IOWA",
    "07491": "JACKSON",
    "05501": "JASPER",
    "08511": "JEFFERSON",
    "06521": "JOHNSON",
    "06531": "JONES",
    "08541": "KEOKUK",
    "03551": "KOSSUTH",
    "08561": "LEE (SOUTH)",
    "08562": "LEE (NORTH)",
    "06571": "LINN",
    "08581": "LOUISA",
    "05591": "LUCAS",
    "03601": "LYON",
    "05611": "MADISON",
    "08621": "MAHASKA",
    "05631": "MARION",
    "02641": "MARSHALL",
    "04651": "MILLS",
    "02661": "MITCHELL",
    "03671": "MONONA",
    "08681": "MONROE",
    "04691": "MONTGOMERY",
    "07701": "MUSCATINE",
    "03711": "OBRIEN",
    "03721": "OSCEOLA",
    "04731": "PAGE",
    "03741": "PALO ALTO",
    "03751": "PLYMOUTH",
    "02761": "POCAHONTAS",
    "05771": "POLK",
    "04781": "POTTAWATTAMIE",
    "08791": "POWESHIEK",
    "05801": "RINGGOLD",
    "02811": "SAC",
    "07821": "SCOTT",
    "04831": "SHELBY",
    "03841": "SIOUX",
    "02851": "STORY",
    "06861": "TAMA",
    "05871": "TAYLOR",
    "05881": "UNION",
    "08891": "VAN BUREN",
    "08901": "WAPELLO",
    "05911": "WARREN",
    "08921": "WASHINGTON",
    "05931": "WAYNE",
    "02941": "WEBSTER",
    "02951": "WINNEBAGO",
    "01961": "WINNESHIEK",
    "03971": "WOODBURY",
    "02981": "WORTH",
    "02991": "WRIGHT"
}

LOOKUP_BY_NAME = {v.replace(" ", "_"): k for k, v in LOOKUP_BY_ID.items()}


def parse(place_id):
    """
    Accepts a place_id and returns the data expected by our target forms
    """
    place_name = place_id[3:].upper()
    place_id = LOOKUP_BY_NAME[place_name]
    return {
        'name': place_name,
        'id': place_id,
    }

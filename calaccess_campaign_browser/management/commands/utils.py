
def parse_election_name(name):
    """
    Translates a raw election name into
    one of our canonical names.
    """
    name = name.upper()
    if 'PRIMARY' in name:
        return 'PRIMARY'
    elif 'GENERAL' in name:
        return 'GENERAL'
    elif 'SPECIAL RUNOFF' in name:
        return 'SPECIAL_RUNOFF'
    elif 'SPECIAL' in name:
        return 'SPECIAL'
    elif 'RECALL' in name:
        return 'RECALL'
    else:
        return 'OTHER'


def parse_office_name(name):
    """
    Translates a raw office name into one of
    our canonical names and a seat (if available).
    """
    seat = None
    name = name.upper()
    if 'LIEUTENANT GOVERNOR' in name:
        office_type = 'LIEUTENANT_GOVERNOR'
    elif 'GOVERNOR' in name:
        office_type = 'GOVERNOR'
    elif 'SECRETARY OF STATE' in name:
        office_type = 'SECRETARY_OF_STATE'
    elif 'CONTROLLER' in name:
        office_type = 'CONTROLLER'
    elif 'TREASURER' in name:
        office_type = 'TREASURER'
    elif 'ATTORNEY GENERAL' in name:
        office_type = 'ATTORNEY_GENERAL'
    elif 'SUPERINTENDENT OF PUBLIC INSTRUCTION' in name:
        office_type = 'SUPERINTENDENT_OF_PUBLIC_INSTRUCTION'
    elif 'INSURANCE COMMISSIONER' in name:
        office_type = 'INSURANCE_COMMISSIONER'
    elif 'MEMBER BOARD OF EQUALIZATION' in name:
        office_type = 'BOARD_OF_EQUALIZATION'
        seat = name.split()[-1]
    elif 'SENATE' in name:
        office_type = 'SENATE'
        seat = name.split()[-1]
    elif 'ASSEMBLY' in name:
        office_type = 'ASSEMBLY'
        seat = name.split()[-1]
    else:
        office_type = 'OTHER'
    return office_type, seat

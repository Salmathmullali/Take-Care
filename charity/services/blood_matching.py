"""Blood type compatibility: whether donor can give to requester."""

# Who can receive from whom (requester blood type -> donor blood types)
COMPATIBILITY = {
    'A+': ['A+', 'A-', 'O+', 'O-'],
    'A-': ['A-', 'O-'],
    'B+': ['B+', 'B-', 'O+', 'O-'],
    'B-': ['B-', 'O-'],
    'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
    'AB-': ['A-', 'B-', 'AB-', 'O-'],
    'O+': ['O+', 'O-'],
    'O-': ['O-'],
}


def is_compatible(donor_blood_type: str, requester_blood_type: str) -> bool:
    allowed_donors = COMPATIBILITY.get(requester_blood_type, [])
    return donor_blood_type in allowed_donors


def filter_compatible_donors(donors, requester_blood_type):
    return [d for d in donors if is_compatible(d.blood_type, requester_blood_type)]

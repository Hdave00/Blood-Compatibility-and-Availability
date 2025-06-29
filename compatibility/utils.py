# using the compatibilty chart here for more modularity cause then i dont need to remake this everywhere, i can just reference it

# source reference canadian blood servies- https://www.blood.ca/en/stories/blood-type-compatibility-which-blood-types-are-compatible-each-other

COMPATIBILITY_CHART = {
    "A+": ["A+", "AB+"],  # Can donate to A+ and AB+
    "A-": ["A+", "A-", "AB+", "AB-"],  # Can donate to A+, A-, AB+, AB-
    "B+": ["B+", "AB+"],  # Can donate to B+ and AB+
    "B-": ["B+", "B-", "AB+", "AB-"],  # Can donate to B+, B-, AB+, AB-
    "AB+": ["AB+"],  # AB+ can only donate to AB+
    "AB-": ["AB+", "AB-"],  # Can donate to AB+ and AB-
    "O+": ["O+", "A+", "B+", "AB+"],  # Can donate to O+, A+, B+, AB+
    "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],  # Can donate to everyone
}

def is_compatible(donor_blood, recipient_blood):
    """ Returns True if donor blood is compatible with recipient blood """

    return recipient_blood in COMPATIBILITY_CHART.get(donor_blood, [])

from collections import namedtuple
from GEMEditor.cobraClasses import Gene, Reaction, Compartment, GeneGroup


def validity_catalyzing_reaction(evidence):
    """ Check if the evidence holds

    Parameters
    ----------
    evidence: Evidence

    Returns
    -------
    bool or None
    """
    if isinstance(evidence.entity, Gene) and isinstance(evidence.target, Reaction):
        return evidence.entity in evidence.target.genes


def validity_not_catalyzing_reaction(evidence):
    """ Check that evidence holds

    Parameters
    ----------
    evidence

    Returns
    -------

    """

    status = validity_catalyzing_reaction(evidence)
    if status is not None:
        return not status


def validity_reversible(evidence):
    """ Check validity of evidence

    Parameters
    ----------
    evidence: Evidence

    Returns
    -------
    bool or None
    """

    if isinstance(evidence.entity, Reaction):
        return evidence.entity.lower_bound < 0. < evidence.entity.upper_bound


def validity_irreversible(evidence):
    """ Check validity of evidence

    Parameters
    ----------
    evidence: Evidence

    Returns
    -------
    bool or None
    """
    status = validity_reversible(evidence)
    if status is not None:
        return not status


def validity_present(evidence):
    """ Check validity of evidence

    Parameters
    ----------
    evidence: Evidence

    Returns
    -------
    bool or None
    """
    if evidence.entity is None:
        return None
    elif isinstance(evidence.entity, Reaction):
        return evidence.entity.lower_bound != 0. or evidence.entity.upper_bound != 0
    else:
        return True


def validity_absence(evidence):
    """ Check validity of evidence

    Parameters
    ----------
    evidence: Evidence

    Returns
    -------
    bool or None
    """
    if evidence.entity is None:
        return None
    elif isinstance(evidence.entity, Reaction):
        reaction = evidence.entity
        return reaction.lower_bound == 0 == reaction.upper_bound
    else:
        return False


def validity_localization(evidence):
    """ Check that evidence holds

    Parameters
    ----------
    evidence: Evidence

    Returns
    -------
    bool or None
    """
    if isinstance(evidence.entity, Gene) and isinstance(evidence.target, Compartment):
        if evidence.entity.reactions:
            for reaction in evidence.entity.reactions:
                if not any(metabolite.compartment == evidence.target.id for metabolite in reaction.metabolites):
                    return False
            return True
        else:
            return False
    else:
        return None


def fix_catalyzing_reaction(evidence):
    gene, reaction = evidence.entity, evidence.target
    if len(reaction._children) == 1:
        child = reaction._children[0]
        if isinstance(child, GeneGroup) and child.type == "or":
            child.add_child(gene)
            return
    reaction.add_child(gene)


def fix_not_catalyzing_reaction(evidence):
    entity = evidence.entity

    for parent in entity._parents.copy():
        if parent is evidence.target:
            parent.remove_child(entity, all=True)
        elif evidence.target in parent.reactions:
            parent.remove_child(entity, all=True)


def fix_reversible(evidence):
    if evidence.entity.lower_bound >= 0.:
        evidence.entity.lower_bound = -1000.
    if evidence.entity.upper_bound <= 0.:
        evidence.entity.upper_bound = 1000.


def fix_irreversible(evidence):
    evidence.entity.lower_bound = 0.


def fix_present(evidence):
    raise NotImplementedError


def fix_absence(evidence):
    raise NotImplementedError


def fix_localization(evidence):
    raise NotImplementedError


# Group contradicting assertions. This list is used in the identification
# of failing evidences and contradicting evidences
assertion = namedtuple("assertion", "text, group, func_validity, func_fix")

ASSERTIONS = [assertion("Catalyzing reaction", 0, validity_catalyzing_reaction, fix_catalyzing_reaction),
              assertion("Not catalyzing reaction", 0, validity_not_catalyzing_reaction, fix_not_catalyzing_reaction),
              assertion("Reversible", 1, validity_reversible, fix_reversible),
              assertion("Irreversible", 1, validity_irreversible, fix_irreversible),
              assertion("Present", 2, validity_present, fix_present),
              assertion("Absent", 2, validity_absence, fix_absence),
              assertion("Localization", 3, validity_localization, fix_localization)]

assertion_to_group = dict((x.text, x.group) for x in ASSERTIONS)

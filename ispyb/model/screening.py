from __future__ import absolute_import, division, print_function

import ispyb.model
from ispyb.model.integration import UnitCell


class Screening(ispyb.model.DBCache):
    """An object representing a Screening database entry.
    The object lazily accesses the underlying database when necessary and
    exposes record data as python attributes.
    """

    def __init__(self, screening_id, db_conn, preload=None):
        """Create a IntegrationResult object for a defined AutoProcIntegrationID.
        Requires a database connection object exposing further data access
        methods.

        :param sceening_id: ScreeningId
        :param db_conn: ISPyB database connection object
        :return: An IntegrationResult object representing the database entry for
                 the specified AutoProcIntegrationID
        """
        self._db = db_conn
        self._screening_id = int(screening_id)
        if preload:
            self._data = preload

    def reload(self):
        """Load/update information from the database."""
        raise NotImplementedError()

    def screening_outputs(self):
        raise NotImplementedError()

ispyb.model.add_properties(
    Screening,
    (
        ("comments", "comments"),
        ("short_comments", "shortComments"),
        ("program_version", "programVersion"),
    ),
)


class ScreeningOutput(ispyb.model.DBCache):

    def __init__(self, output_id, db_conn, preload=None):
        self._db = db_conn
        self._output_id = output_id
        if preload:
            self._data = preload

    def reload(self):
        """Load/update information from the database."""
        raise NotImplementedError()

    def lattices(self):
        raise NotImplementedError()


ispyb.model.add_properties(
    ScreeningOutput,
    (
        ("alignment_success", "alignmentSuccess"),
        ("indexing_success", "indexingSuccess"),
        ("strategy_success", "strategySuccess"),
        ("program", "program"),
    ),
)


class ScreeningOutputLattice(ispyb.model.DBCache):

    def __init__(self, lattice_id, db_conn, preload=None):
        self._db = db_conn
        self._lattice_id = lattice_id
        if preload:
            self._data = preload

    def reload(self):
        """Load/update information from the database."""
        raise NotImplementedError()

    @property
    def unit_cell(self):
        """Returns the unit cell model"""
        return ispyb.model.integration.UnitCell(
            self._data["unitCell_a"],
            self._data["unitCell_b"],
            self._data["unitCell_c"],
            self._data["unitCell_alpha"],
            self._data["unitCell_beta"],
            self._data["unitCell_gamma"],
        )

ispyb.model.add_properties(
    ScreeningOutputLattice,
    (
        ("spacegroup", "spaceGroup"),
    ),
)
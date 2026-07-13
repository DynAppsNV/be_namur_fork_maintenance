# Copyright 2025 Dynapps
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestStageTransitionTour(HttpCase):
    def test_stage_transition_tour(self):
        """GUI: the get_view-injected transition button renders, clicking it
        moves the request to the target stage, and the button then hides."""
        stage_to = self.env["maintenance.stage"].create(
            {"name": "Tour To Stage", "sequence": 20}
        )
        stage_from = self.env["maintenance.stage"].create(
            {
                "name": "Tour From Stage",
                "sequence": 10,
                "next_stage_ids": [(4, stage_to.id)],
            }
        )
        request = self.env["maintenance.request"].create(
            {"name": "Tour Request", "stage_id": stage_from.id}
        )
        self.start_tour(
            "/web#id=%d&model=maintenance.request&view_type=form" % request.id,
            "maintenance_stage_transition_tour",
            login="admin",
        )
        self.assertEqual(request.stage_id, stage_to)

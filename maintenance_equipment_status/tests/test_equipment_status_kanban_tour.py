# Copyright 2025 Dynapps
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestEquipmentStatusKanbanTour(HttpCase):
    def test_equipment_status_kanban_tour(self):
        """GUI: the rebuilt equipment kanban card renders and the status badge
        shows the demo equipment's status value ("New")."""
        # Guard: the assertion depends on the demo status being present.
        status_new = self.env.ref(
            "maintenance_equipment_status.maintenance_equipment_status_1"
        )
        equipment = self.env.ref("maintenance.equipment_monitor1")
        self.assertEqual(equipment.status_id, status_new)
        self.assertEqual(status_new.name, "New")
        self.start_tour(
            "/odoo/action-maintenance.hr_equipment_action",
            "maintenance_equipment_status_kanban_tour",
            login="admin",
        )

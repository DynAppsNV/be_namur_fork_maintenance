# Copyright 2019 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as test_common
from odoo import fields
from odoo.exceptions import ValidationError


class TestMaintenanceTimesheet(test_common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.stage_undone = self.env.ref("maintenance.stage_0")
        self.stage_done = self.env.ref("maintenance.stage_4")

        self.request_demo1 = self.env.ref("maintenance_timesheet.request_1")
        self.request2 = self.env["maintenance.request"].create(
            {
                "name": "Corrective #2 for Generic Monitor",
                "equipment_id": self.env.ref("maintenance_project.equipment_1").id,
                "user_id": self.env.ref("base.user_admin").id,
                "schedule_date": fields.Date.today(),
                "stage_id": self.stage_undone.id,
                "maintenance_type": "corrective",
            }
        )
        self.timesheet21_data = {
            "name": "Some tasks done",
            "project_id": self.request2.project_id.id,
            "user_id": self.env.ref("base.user_admin").id,
            "date": fields.Date.today(),
            "unit_amount": 1.5,
        }
        self.request2.timesheet_ids = [(0, 0, self.timesheet21_data)]

    def test_request_timesheets(self):
        self.assertEqual(self.request_demo1.timesheet_total_hours, 2)
        self.assertEqual(
            self.request2.timesheet_total_hours, self.timesheet21_data["unit_amount"]
        )

    def test_write_multi_record_different_requests(self):
        """Writing a recordset of timesheets linked to different (not-done)
        requests must not raise a singleton error."""
        ts1 = self.request2.timesheet_ids[:1]
        ts2 = self.env["account.analytic.line"].create(
            {
                "name": "Other request work",
                "project_id": self.request_demo1.project_id.id,
                "maintenance_request_id": self.request_demo1.id,
                "user_id": self.env.ref("base.user_admin").id,
                "date": fields.Date.today(),
                "unit_amount": 1.0,
            }
        )
        combined = ts1 | ts2
        self.assertEqual(
            combined.mapped("maintenance_request_id"),
            self.request2 | self.request_demo1,
        )
        combined.write({"unit_amount": 2.0})
        self.assertEqual(ts1.unit_amount, 2.0)
        self.assertEqual(ts2.unit_amount, 2.0)

    def test_onchange_maintenance_request_id(self):
        ts1 = self.env["account.analytic.line"].new(
            {
                "date": fields.Date.today(),
                "name": "Timesheet without initial equipment",
                "user_id": self.env.ref("base.user_admin").id,
            }
        )
        self.assertFalse(ts1.project_id)
        ts1.maintenance_request_id = self.request2
        ts1.onchange_maintenance_request_id()
        self.assertEqual(ts1.project_id, self.request2.project_id)

    def test_check_request_done(self):
        self.request2.stage_id = self.stage_done
        with self.assertRaises(ValidationError):
            self.request2.timesheet_ids = [
                (
                    0,
                    0,
                    {
                        "name": "Attempt to create a task for a done request",
                        "project_id": self.request2.project_id.id,
                        "user_id": self.env.ref("base.user_admin").id,
                        "date": fields.Date.today(),
                        "unit_amount": 2,
                    },
                )
            ]
        with self.assertRaises(ValidationError):
            self.env["account.analytic.line"].create(
                {
                    "name": "Attepting to create a task 2",
                    "project_id": self.request2.project_id.id,
                    "user_id": self.env.ref("base.user_admin").id,
                    "maintenance_request_id": self.request2.id,
                    "date": fields.Date.today(),
                    "unit_amount": 1,
                }
            )
        with self.assertRaises(ValidationError):
            # Attempt to modify a timesheet related a done request
            for timesheet in self.request2.timesheet_ids:
                timesheet.unit_amount += 1
        with self.assertRaises(ValidationError):
            # Attempt to delete a timesheet related a done request
            self.request2.timesheet_ids.unlink()

        self.request2.stage_id = self.stage_undone
        # Deleting timesheets is enabled again
        self.request2.timesheet_ids.unlink()

    def test_action_view_timesheet_ids(self):
        act1 = self.request2.action_view_timesheet_ids()
        self.assertEqual(act1["domain"][0][2], self.request2.id)
        self.assertEqual(
            act1["context"]["default_project_id"], self.request2.project_id.id
        )
        self.assertFalse(act1["context"]["default_task_id"])
        self.assertFalse(act1["context"]["readonly_employee_id"])

    def test_prepare_project_from_equipment_values(self):
        data = self.env["maintenance.equipment"]._prepare_project_from_equipment_values(
            {"name": "my name"}
        )
        self.assertTrue(data["allow_timesheets"])

    def test_action_create_project_no_values_with_timesheet(self):
        """action_create_project() calls _prepare_project_from_equipment_values
        with no argument; the timesheet override must accept that and still flag
        the project for timesheets."""
        equipment = self.env["maintenance.equipment"].create(
            {"name": "Equipment needing a project"}
        )
        self.assertFalse(equipment.project_id)
        equipment.action_create_project()
        self.assertTrue(equipment.project_id)
        self.assertEqual(equipment.project_id.name, "Equipment needing a project")
        self.assertTrue(equipment.project_id.allow_timesheets)

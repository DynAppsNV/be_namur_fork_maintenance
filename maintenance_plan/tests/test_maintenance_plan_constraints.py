# Copyright 2025 Dynapps
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError

from odoo.exceptions import UserError, ValidationError
from odoo.tools import mute_logger

from .common import TestMaintenancePlanBase


class TestMaintenancePlanConstraints(TestMaintenancePlanBase):
    @mute_logger("odoo.sql_db")
    def test_equipment_kind_unique_constraint(self):
        """equipment_kind_uniq: a second plan for the same equipment + kind is
        rejected (maintenance_plan_2 already uses equipment_1 + weekly_kind)."""
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.maintenance_plan_obj.create(
                {
                    "equipment_id": self.equipment_1.id,
                    "maintenance_kind_id": self.weekly_kind.id,
                    "interval": 1,
                    "interval_step": "week",
                }
            )
            self.env.flush_all()

    def test_equipment_kind_unique_allows_other_kind(self):
        """A different kind on the same equipment is accepted."""
        new_kind = self.env["maintenance.kind"].create({"name": "Biweekly check"})
        plan = self.maintenance_plan_obj.create(
            {
                "equipment_id": self.equipment_1.id,
                "maintenance_kind_id": new_kind.id,
                "interval": 2,
                "interval_step": "week",
            }
        )
        self.assertEqual(plan.maintenance_kind_id, new_kind)
        self.assertEqual(plan.equipment_id, self.equipment_1)

    @mute_logger("odoo.sql_db")
    def test_kind_name_unique_constraint(self):
        """maintenance.kind name_uniq: duplicate kind name is rejected."""
        self.env["maintenance.kind"].create({"name": "Quarterly review"})
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.env["maintenance.kind"].create({"name": "Quarterly review"})
            self.env.flush_all()

    def test_plan_company_must_match_equipment_company(self):
        """_check_company_id: a plan whose company differs from its equipment's
        company raises ValidationError."""
        company_b = self.env["res.company"].create({"name": "Maintenance Co B"})
        equipment_b = self.maintenance_equipment_obj.create(
            {"name": "Equipment in B", "company_id": company_b.id}
        )
        self.assertNotEqual(self.env.company, company_b)
        with self.assertRaises(ValidationError):
            self.maintenance_plan_obj.create(
                {
                    "equipment_id": equipment_b.id,
                    "company_id": self.env.company.id,
                    "interval": 1,
                    "interval_step": "month",
                }
            )

    def test_plan_company_matching_equipment_company_ok(self):
        """_check_company_id: equal companies pass the constraint."""
        equipment = self.maintenance_equipment_obj.create(
            {"name": "Same-company equipment", "company_id": self.env.company.id}
        )
        plan = self.maintenance_plan_obj.create(
            {
                "equipment_id": equipment.id,
                "company_id": self.env.company.id,
                "interval": 1,
                "interval_step": "month",
            }
        )
        self.assertEqual(plan.company_id, self.env.company)

    def test_unlink_blocked_when_open_preventive_request_exists(self):
        """unlink() refuses to drop a plan that has generated a not-done
        preventive request of its kind."""
        self.maintenance_plan_2.button_manual_request_generation()
        open_requests = self.maintenance_request_obj.search(
            [
                ("maintenance_plan_id", "=", self.maintenance_plan_2.id),
                ("maintenance_kind_id", "=", self.weekly_kind.id),
                ("stage_id.done", "=", False),
                ("maintenance_type", "=", "preventive"),
            ]
        )
        self.assertTrue(open_requests)
        with self.assertRaises(UserError):
            self.maintenance_plan_2.unlink()

    def test_unlink_allowed_without_requests(self):
        """A plan that has generated no request passes the unlink guard and is
        deleted."""
        new_kind = self.env["maintenance.kind"].create({"name": "Ad-hoc check"})
        plan = self.maintenance_plan_obj.create(
            {
                "equipment_id": self.equipment_1.id,
                "maintenance_kind_id": new_kind.id,
                "interval": 1,
                "interval_step": "year",
            }
        )
        plan_id = plan.id
        self.assertFalse(plan.maintenance_ids)
        plan.unlink()
        self.assertFalse(self.maintenance_plan_obj.browse(plan_id).exists())

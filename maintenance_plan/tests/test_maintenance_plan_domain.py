# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo.addons.maintenance_plan.tests.common import TestMaintenancePlanBase


class TestMaintenancePlanDomain(TestMaintenancePlanBase):
    def test_search_equipment_id_operators(self):
        """The search_equipment_id custom search must accept both "=" and the
        "in" form (v19's optimizer normalises "=" to an "in" with an OrderedSet),
        without raising. Regression for the equipment view crash on v19."""
        Plan = self.maintenance_plan_obj
        eq_result = Plan.search(
            [("search_equipment_id", "=", self.equipment_1.id)]
        )
        # plans 1-3 target equipment_1 directly; plan_4 has no equipment.
        self.assertIn(self.maintenance_plan_1, eq_result)
        self.assertIn(self.maintenance_plan_2, eq_result)
        self.assertIn(self.maintenance_plan_3, eq_result)
        self.assertNotIn(self.maintenance_plan_4, eq_result)
        in_result = Plan.search(
            [("search_equipment_id", "in", [self.equipment_1.id])]
        )
        self.assertEqual(eq_result, in_result)

    def test_generate_requests_no_domain(self):
        self.maintenance_plan_obj.cron_create_maintenance_requests()
        generated_requests = self.maintenance_request_obj.search(
            [("maintenance_plan_id", "=", self.maintenance_plan_5.id)],
            order="schedule_date asc",
        )

        self.assertEqual(len(generated_requests), 3)
        self.assertFalse(generated_requests.mapped("equipment_id"))

    def test_generate_requests_domain(self):
        equipment_2 = self.maintenance_equipment_obj.create({"name": "Laptop 2"})
        self.maintenance_plan_5.write(
            {
                "generate_with_domain": True,
                "generate_domain": json.dumps(
                    [("id", "in", [equipment_2.id, self.equipment_1.id])]
                ),
            }
        )
        self.maintenance_plan_obj.cron_create_maintenance_requests()
        generated_requests = self.maintenance_request_obj.search(
            [("maintenance_plan_id", "=", self.maintenance_plan_5.id)],
            order="schedule_date asc",
        )

        self.assertEqual(len(generated_requests), 6)
        self.assertIn(equipment_2, generated_requests.mapped("equipment_id"))
        self.assertIn(self.equipment_1, generated_requests.mapped("equipment_id"))

    def test_generate_requests_domain_per_equipment_distribution(self):
        """Each matched equipment gets its own full horizon (3 requests), not a
        shared/cross-contaminated set: 3 + 3, never 2 + 4."""
        equipment_2 = self.maintenance_equipment_obj.create({"name": "Laptop 2"})
        self.maintenance_plan_5.write(
            {
                "generate_with_domain": True,
                "generate_domain": json.dumps(
                    [("id", "in", [equipment_2.id, self.equipment_1.id])]
                ),
            }
        )
        self.maintenance_plan_obj.cron_create_maintenance_requests()
        requests = self.maintenance_request_obj.search(
            [("maintenance_plan_id", "=", self.maintenance_plan_5.id)]
        )
        per_equipment = {
            self.equipment_1: requests.filtered(
                lambda r: r.equipment_id == self.equipment_1
            ),
            equipment_2: requests.filtered(lambda r: r.equipment_id == equipment_2),
        }
        self.assertEqual(len(per_equipment[self.equipment_1]), 3)
        self.assertEqual(len(per_equipment[equipment_2]), 3)

    def test_generate_requests_is_idempotent(self):
        """Running the cron twice does not create duplicate open requests while
        the first batch is still not done."""
        equipment_2 = self.maintenance_equipment_obj.create({"name": "Laptop 2"})
        self.maintenance_plan_5.write(
            {
                "generate_with_domain": True,
                "generate_domain": json.dumps(
                    [("id", "in", [equipment_2.id, self.equipment_1.id])]
                ),
            }
        )
        self.maintenance_plan_obj.cron_create_maintenance_requests()
        first_run = self.maintenance_request_obj.search(
            [("maintenance_plan_id", "=", self.maintenance_plan_5.id)]
        )
        self.assertEqual(len(first_run), 6)
        self.maintenance_plan_obj.cron_create_maintenance_requests()
        second_run = self.maintenance_request_obj.search(
            [("maintenance_plan_id", "=", self.maintenance_plan_5.id)]
        )
        self.assertEqual(second_run, first_run)

    def test_button_generation_expands_domain(self):
        """The manual button expands a domain plan per matched equipment, the
        same as the cron (no equipment-less requests)."""
        equipment_2 = self.maintenance_equipment_obj.create({"name": "Laptop 2"})
        self.maintenance_plan_5.write(
            {
                "generate_with_domain": True,
                "generate_domain": json.dumps(
                    [("id", "in", [equipment_2.id, self.equipment_1.id])]
                ),
            }
        )
        self.maintenance_plan_5.button_manual_request_generation()
        requests = self.maintenance_request_obj.search(
            [("maintenance_plan_id", "=", self.maintenance_plan_5.id)]
        )
        self.assertEqual(len(requests), 6)
        self.assertEqual(
            requests.mapped("equipment_id"), self.equipment_1 | equipment_2
        )
        self.assertFalse(requests.filtered(lambda r: not r.equipment_id))

    def test_cron_isolates_a_failing_plan(self):
        """A plan whose generate_domain raises must not abort generation for the
        other plans (per-plan savepoint)."""
        broken = self.maintenance_plan_obj.create(
            {
                "start_maintenance_date": "2023-01-25",
                "interval": 1,
                "interval_step": "month",
                "maintenance_plan_horizon": 2,
                "planning_step": "month",
                "generate_with_domain": True,
                "generate_domain": "undefined_name_boom",  # raises in safe_eval
            }
        )
        # Must not raise, despite the broken plan.
        self.maintenance_plan_obj.cron_create_maintenance_requests()
        good = self.maintenance_request_obj.search(
            [("maintenance_plan_id", "=", self.maintenance_plan_1.id)]
        )
        self.assertEqual(len(good), 3)
        broken_reqs = self.maintenance_request_obj.search(
            [("maintenance_plan_id", "=", broken.id)]
        )
        self.assertFalse(broken_reqs)

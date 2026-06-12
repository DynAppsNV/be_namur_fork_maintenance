# Copyright 2025 Dynapps
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError

from odoo.tests import TransactionCase
from odoo.tools import mute_logger


class TestMaintenanceEquipmentTag(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Tag = cls.env["maintenance.equipment.tag"]
        cls.Equipment = cls.env["maintenance.equipment"]
        cls.tag = cls.Tag.create({"name": "Servers"})
        cls.equipment_a = cls.Equipment.create({"name": "Server A"})
        cls.equipment_b = cls.Equipment.create({"name": "Server B"})

    def test_color_default_within_palette_range(self):
        """get_default_color_value uses randint(1, 15): every default color
        must land inside the 1..15 kanban palette."""
        colors = [
            self.Tag.create({"name": "Palette %s" % i}).color for i in range(16)
        ]
        for color in colors:
            self.assertGreaterEqual(color, 1)
            self.assertLessEqual(color, 15)

    def test_explicit_color_overrides_default(self):
        """An explicit color is kept and not replaced by the random default."""
        tag = self.Tag.create({"name": "Fixed", "color": 7})
        self.assertEqual(tag.color, 7)

    @mute_logger("odoo.sql_db")
    def test_name_unique_constraint_blocks_duplicate(self):
        """The name_uniq SQL constraint rejects a second tag with the same name."""
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.Tag.create({"name": "Servers"})
            self.env.flush_all()

    def test_name_unique_constraint_allows_distinct(self):
        """A different name is accepted (boundary of the unique constraint)."""
        other = self.Tag.create({"name": "Workstations"})
        self.assertEqual(other.name, "Workstations")
        self.assertNotEqual(other, self.tag)

    def test_equipment_many2many_membership_and_search(self):
        """equipment_ids holds the exact linked set and is searchable, with
        unrelated tags excluded."""
        self.tag.equipment_ids = self.equipment_a | self.equipment_b
        self.assertEqual(
            self.tag.equipment_ids, self.equipment_a | self.equipment_b
        )
        unlinked = self.Tag.create({"name": "Unlinked"})
        found = self.Tag.search([("equipment_ids", "in", self.equipment_a.ids)])
        self.assertIn(self.tag, found)
        self.assertNotIn(unlinked, found)

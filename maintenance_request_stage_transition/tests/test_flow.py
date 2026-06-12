# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from lxml import etree

from odoo.tests.common import TransactionCase
from odoo.tools.safe_eval import safe_eval


class TestFlow(TransactionCase):
    def setUp(self):
        super().setUp()
        self.request = self.env["maintenance.request"].create({"name": "Request"})
        self.original_stage = self.request.stage_id
        self.last_stage = self.env["maintenance.stage"].create({"name": "Last state"})
        self.stage = self.env["maintenance.stage"].create(
            {"name": "New state", "next_stage_ids": [(4, self.last_stage.id)]}
        )
        self.original_stage.write({"next_stage_ids": [(4, self.stage.id)]})

    def test_inverse(self):
        self.assertIn(self.original_stage, self.stage.previous_stage_ids)

    def get_button(self, stage):
        data = self.request.get_view(view_type="form")
        form = etree.XML(data["arch"])
        path = "//header/button[@name='set_maintenance_stage' and @id='%s']"
        button = form.xpath(path % stage.id)[0]
        self.assertTrue(etree.iselement(button))
        return button

    def _is_invisible(self, button):
        # v17+ stores the modifier as a python expression on ``invisible``
        # referencing the record fields instead of the legacy ``attrs`` domain.
        return bool(
            safe_eval(
                button.attrib["invisible"],
                {"stage_id": self.request.stage_id.id},
            )
        )

    def test_nochange(self):
        self.request.set_maintenance_stage()
        self.assertEqual(self.original_stage, self.request.stage_id)

    def test_form(self):
        button_stage = self.get_button(self.stage)
        button_last = self.get_button(self.last_stage)
        # self.stage is reachable from the current stage -> button visible,
        # last_stage is not -> button hidden.
        self.assertFalse(self._is_invisible(button_stage))
        self.assertTrue(self._is_invisible(button_last))
        # Perform the transition advertised by the visible button.
        getattr(
            self.request.with_context(**json.loads(button_stage.attrib["context"])),
            button_stage.attrib["name"],
        )()
        self.request.invalidate_recordset()
        self.assertEqual(self.request.stage_id, self.stage)
        # After moving, visibility flips for both buttons.
        self.assertTrue(self._is_invisible(button_stage))
        self.assertFalse(self._is_invisible(button_last))

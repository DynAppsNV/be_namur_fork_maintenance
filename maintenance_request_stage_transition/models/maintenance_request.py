# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MaintenanceRequest(models.Model):

    _inherit = "maintenance.request"

    stage_id = fields.Many2one("maintenance.stage", readonly=True)

    @api.model
    def get_view(self, view_id=None, view_type="form", **options):
        res = super().get_view(view_id=view_id, view_type=view_type, **options)
        if view_type == "form":
            doc = etree.XML(res["arch"])
            headers = doc.xpath("//form/header")
            if headers:
                stages = self.env["maintenance.stage"].search(
                    [], order="sequence desc"
                )
                header = headers[0]
                for stage in stages:
                    header.insert(0, stage._get_stage_node())
                res["arch"] = etree.tostring(doc, encoding="unicode")
        return res

    def set_maintenance_stage(self):
        if not self.env.context.get("next_stage_id"):
            return {}
        return self._set_maintenance_stage(self.env.context.get("next_stage_id"))

    def _set_maintenance_stage(self, stage_id):
        # The UI "invisible" modifier only hides invalid buttons; enforce the
        # allowed transition server-side too (and guard against multi/scripted
        # callers writing the same target to unrelated requests).
        self.ensure_one()
        target = self.env["maintenance.stage"].browse(stage_id)
        if target not in self.stage_id.next_stage_ids:
            raise UserError(
                _(
                    "Cannot move %(req)s to stage %(stage)s: it is not an "
                    "allowed next stage from %(current)s.",
                    req=self.display_name,
                    stage=target.display_name,
                    current=self.stage_id.display_name,
                )
            )
        self.write({"stage_id": stage_id})

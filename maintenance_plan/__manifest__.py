# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Maintenance Plan",
    "summary": "Extends preventive maintenance planning",
    "version": "18.0.0.0",
    "author": "Camptocamp SA, ForgeFlow, Odoo Community Association (Forked by Dynapps)",
    "license": "AGPL-3",
    "category": "Maintenance",
    "website": "https://github.com/OCA/maintenance",
    "images": [],
    "depends": ["base_maintenance"],
    "data": [
        "security/ir.model.access.csv",
        "security/maintenance_security.xml",
        "data/ir_cron.xml",
        "views/maintenance_kind_views.xml",
        "views/maintenance_plan_views.xml",
        "views/maintenance_equipment_views.xml",
        "views/report_maintenance_request.xml",

        "data/ir_actions_server.xml",
        "views/res_config_settings.xml",
    ],
    "external_dependencies": {"python": ["python-dateutil"]},
    "demo": ["demo/demo_maintenance_plan.xml"],
    "installable": True,
}

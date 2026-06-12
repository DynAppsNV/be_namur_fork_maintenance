# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Maintenance Request Stage transition",
    "summary": """
        Manage transition visibility and management between stages""",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/maintenance",
    "depends": ["maintenance"],
    "data": ["views/maintenance_request.xml", "views/maintenance_stage.xml"],
    "demo": ["data/demo_maintenance_request_stage_transition.xml"],
    "assets": {
        "web.assets_tests": [
            "maintenance_request_stage_transition/static/tests/tours/stage_transition_tour.esm.js",
        ],
    },
    "maintainers": ["etobella"],
    "installable": True,
}

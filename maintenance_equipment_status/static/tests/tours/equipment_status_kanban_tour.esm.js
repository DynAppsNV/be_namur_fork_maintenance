import {registry} from "@web/core/registry";

/* The equipment kanban card was rebuilt for the v17+ OWL card template; this
 * confirms it renders and that the status badge (t-out of status_id) shows the
 * demo equipment's status value instead of crashing the card. */
registry.category("web_tour.tours").add("maintenance_equipment_status_kanban_tour", {
    steps: () => [
        {
            content: "Equipment kanban renders cards",
            trigger: ".o_kanban_renderer .o_kanban_record",
        },
        {
            content: "A card shows the status badge with the demo status value",
            trigger: ".o_kanban_record .badge:contains('New')",
        },
    ],
});

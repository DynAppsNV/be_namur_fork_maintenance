import {registry} from "@web/core/registry";

/* Drives the maintenance request form: the dynamically injected
 * "To <stage>" button (built by get_view) must be visible for a reachable
 * stage, clicking it must transition the record, and afterwards the button
 * must disappear because the modifier recomputes against the new stage. */
registry.category("web_tour.tours").add("maintenance_stage_transition_tour", {
    steps: () => [
        {
            content: "The reachable transition button is rendered in the header",
            trigger:
                "button[name='set_maintenance_stage']:contains('Tour To Stage')",
            run: "click",
        },
        {
            content: "Statusbar now shows the request in the target stage",
            trigger:
                ".o_statusbar_status button.o_arrow_button_current:contains('Tour To Stage')",
        },
        {
            content: "The transition button to that stage is gone (modifier recomputed)",
            trigger: "body:not(:has(button[name='set_maintenance_stage']:contains('Tour To Stage')))",
        },
    ],
});

/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";


export const amont_license_client = {
    dependencies: ["bus_service", "notification", "action"],

    start(env, { bus_service, notification, action }) {
        bus_service.subscribe("amont_license_client", ({ message, sticky, title, type }) => {
            notification.add(message, { sticky, title, type });
        });
    }
};

registry.category("services").add("amont_license_client", amont_license_client);

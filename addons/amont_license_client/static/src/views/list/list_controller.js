/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";

patch(ListController.prototype, {
    async onclickCreate() {
        console.log("Create button clicked in Amont License Client List Controller");
    }
})
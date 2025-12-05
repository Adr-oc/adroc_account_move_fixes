/** @odoo-module **/

import { BankRecKanbanRenderer } from "@account_accountant/components/bank_reconciliation/kanban_renderer";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";
import { onWillStart, useState } from "@odoo/owl";

patch(BankRecKanbanRenderer.prototype, {
    setup() {
        super.setup();
        this.permissionState = useState({
            canViewBalanceSummary: false,
        });

        onWillStart(async () => {
            this.permissionState.canViewBalanceSummary = await user.hasGroup(
                "adroc_account_move_fixes.group_bank_reconciliation_balance_summary"
            );
        });
    },

    get canViewBalanceSummary() {
        return this.permissionState.canViewBalanceSummary;
    },
});

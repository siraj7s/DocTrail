// Copyright (c) 2026, siraj.panigrahi@atriina.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Document View Request', {
    setup: function (frm) {

        // Prevent duplicate Managed Document selection
        frm.set_query('document', 'documents', function (doc, cdt, cdn) {
            let selected_docs = (frm.doc.documents || [])
                .map(row => row.document)
                .filter(d => d);

            return {
                filters: [
                    ['name', 'not in', selected_docs]
                ]
            };
        });
    },
    onload: function (frm) {
        if (frm.is_new() && !frm.doc.employee_id) {
            frappe.db.get_value("Employee",
                { user_id: frappe.session.user },
                "name"
            ).then(r => {
                if (r.message && r.message.name) {
                    frm.set_value("employee_id", r.message.name);
                } else {
                    frappe.msgprint("No Employee linked to this User.");
                }
            });
        }
    },
    refresh: function (frm) {

        if (frm.doc.workflow_state === "Approved") {

            // Make all fields read only
            frm.fields.forEach(field => {
                frm.set_df_property(field.df.fieldname, 'read_only', 1);
            });

            // Allow only time_in and time_out
            frm.set_df_property('time_in', 'read_only', 0);
            frm.set_df_property('time_out', 'read_only', 0);

        } else {

            // Make fields editable again if not Approved
            frm.fields.forEach(field => {
                frm.set_df_property(field.df.fieldname, 'read_only', 0);
            });
        }

        const workflow = frm.doc.workflow_state;

        const is_approver = frappe.user.has_role("Archive Approver");
        const is_librarian = frappe.user.has_role("Archive Librarian");

        // -------------------------
        // Default: make both read-only
        // -------------------------
        frm.set_df_property('remark_by_approver', 'read_only', 1);
        frm.set_df_property('remark_by_librarian', 'read_only', 1);
        frm.set_df_property('document_series', 'read_only', 1);

        // -------------------------
        // Sent For Approval + Archive Approver
        // -------------------------
        if (workflow === "Sent For Approval" && is_approver) {
            frm.set_df_property('remark_by_approver', 'read_only', 0);
        }

        // -------------------------
        // Approved + Archive Librarian
        // -------------------------
        if (workflow === "Approved" && is_librarian) {
            frm.set_df_property('remark_by_librarian', 'read_only', 0);
        }
    }
});

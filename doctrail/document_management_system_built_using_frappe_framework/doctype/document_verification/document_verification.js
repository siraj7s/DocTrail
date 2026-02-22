// Copyright (c) 2026, sirajpanigrahi@gail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Document Verification', {
    setup: function (frm) {

        // Prevent duplicate Managed Document selection
        frm.set_query('document', 'documents', function (doc, cdt, cdn) {
            let selected_docs = (frm.doc.documents || [])
                .map(row => row.document)
                .filter(d => d);

            return {
                filters: [
                    ['Document Registration', 'name', 'not in', selected_docs]
                ]
            };
        });
    },

    onload: function (frm) {
        if (frm.is_new() && !frm.doc.verified_by) {
            frm.set_value('date', frappe.datetime.get_today());
            frappe.db.get_value("Employee",
                { user_id: frappe.session.user },
                "name"
            ).then(r => {
                if (r.message && r.message.name) {
                    frm.set_value("verified_by", r.message.name);
                } else {
                    frappe.msgprint("No Employee linked to this User.");
                }
            });

        }
    }
});
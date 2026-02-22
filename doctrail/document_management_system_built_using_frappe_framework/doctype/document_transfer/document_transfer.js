// Copyright (c) 2026, sirajpanigrahi@gail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Document Transfer', {
    setup: function (frm) {

        // Prevent duplicate documents in child table
        frm.set_query('document', 'documents', function (doc, cdt, cdn) {
            let selected_docs = (frm.doc.documents || [])
                .map(d => d.document)
                .filter(d => d);

            return {
                filters: [
                    ['Document Registration', 'name', 'not in', selected_docs]
                    // ['Managed Document', 'group', '=', frm.doc.group],
                    // ['Managed Document', 'year', '=', frm.doc.year],
                    // ['Managed Document', 'shelf', '=', frm.doc.shelf]
                ]
            };
        });
    },

    onload: function (frm) {
        if (frm.is_new()) {
            frm.set_value('date_of_transfer', frappe.datetime.get_today());
            frappe.db.get_value("Employee",
                { user_id: frappe.session.user },
                "name"
            ).then(r => {
                if (r.message && r.message.name) {
                    frm.set_value("approved_by", r.message.name);
                } else {
                    frappe.msgprint("No Employee linked to this User.");
                }
            });
        }
    }
});

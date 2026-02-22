// Copyright (c) 2026, sirajpanigrahi@gail.com and contributors
// For license information, please see license.txt

frappe.ui.form.on('Document Received', {
    onload: function (frm) {
        if (frm.is_new() && !frm.doc.received_by) {
            frappe.db.get_value("Employee",
                { user_id: frappe.session.user },
                "name"
            ).then(r => {
                if (r.message && r.message.name) {
                    frm.set_value("received_by", r.message.name);
                } else {
                    frappe.msgprint("No Employee linked to this User.");
                }
            });
        }
        set_rack_filter(frm);
    },
    refresh: function (frm) {
        const is_librarian = frappe.user.has_role("Archive Librarian");
        // Editable only for Archive Librarian
        frm.set_df_property(
            'remarks',
            'read_only',
            !is_librarian
        );
    }
});

function set_rack_filter(frm) {
    frm.set_query('rack', function () {
        if (!frm.doc.shelf) {
            return {};
        }

        return {
            filters: {
                shelf: frm.doc.shelf
            }
        };
    });

}

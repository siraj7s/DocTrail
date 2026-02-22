frappe.ui.form.on('Document Registration', {
    onload: function (frm) {
        if (frm.is_new()) {
            // Set Registered By (Employee linked to logged-in user)
            if (!frm.doc.registered_by) {
                frappe.db.get_value("Employee",
                    { user_id: frappe.session.user },
                    "name"
                ).then(r => {
                    if (r.message && r.message.name) {
                        frm.set_value("registered_by", r.message.name);
                    } else {
                        frappe.msgprint("No Employee linked with this User.");
                    }
                });
            }
            if (!frm.doc.registration_date) {
                frm.set_value('registration_date', frappe.datetime.get_today());
            }

            // Set Shelf Filter
            set_rack_filter(frm);
        }
    },
    department_of_employee: function (frm) {
        set_rack_filter(frm);
    },
    volume_applicable: function (frm) {
        update_document_name(frm);
    },
    document_name: function (frm) {
        update_document_name(frm);
    },
    volume_no: function (frm) {
        update_document_name(frm);
    },
    volume_range: function (frm) {
        update_document_name(frm);
    },
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

function update_document_name(frm) {
    if (!frm.doc.document_name) return;
    let base = frm.doc.document_name.split('-')[0];
    if (frm.doc.volume_applicable && frm.doc.volume_no) {
        let new_name = `${base}-${frm.doc.volume_no}`;
        frm.set_value('document_name', new_name);
    } else {
        frm.set_value('document_name', base);
    }
}

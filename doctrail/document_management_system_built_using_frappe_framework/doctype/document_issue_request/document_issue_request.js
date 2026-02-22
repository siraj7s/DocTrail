frappe.ui.form.on('Document Issue Request', {
    refresh: function (frm) {
        if (frm.is_new() && !frm.doc.employee_id) {

            frappe.db.get_value(
                'Employee',
                { user_id: frappe.session.user },
                ['name'],
                function (r) {
                    if (r && r.name) {
                        frm.set_value('employee_id', r.name);
                    } else {
                        frappe.msgprint("No Employee linked with this User.");
                    }
                }
            );
        }

        // Trigger only when workflow state is Returned
        if (frm.doc.workflow_state === "Returned" && !frm.is_new()) {

            // Small delay to avoid multiple redirects
            setTimeout(() => {

                frappe.new_doc("Document Received", {
                    issue_id: frm.doc.name,
                    employee_id: frm.doc.employee_id,
                    received_by: frappe.session.user_fullname,
                    date_of_return: frappe.datetime.get_today()
                });

            }, 500);
        }

        const workflow = frm.doc.workflow_state;
        const is_approver = frappe.user.has_role("Archive Approver");
        const is_librarian = frappe.user.has_role("Archive Librarian");

        // Default: Make both read-only
        frm.set_df_property('remark_by_approver', 'read_only', 1);
        frm.set_df_property('remark_by_librarian', 'read_only', 1);

        // Requested + Archive Approver
        if (workflow === "Requested" && is_approver) {
            frm.set_df_property('remark_by_approver', 'read_only', 0);
        }

        // Approved + Archive Librarian
        if (workflow === "Approved" && is_librarian) {
            frm.set_df_property('remark_by_librarian', 'read_only', 0);
        }
    },
});


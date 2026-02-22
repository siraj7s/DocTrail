# Copyright (c) 2026, sirajpanigrahi@gail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DocumentReceived(Document):
    def after_insert(self):
        # Get Employee linked to logged-in user
        employee = frappe.db.get_value(
            "Employee",
            {"user_id": frappe.session.user},
            "name"
        )
        if employee:
            self.db_set("received_by", employee, update_modified=False)
        else:
            frappe.throw("No Employee linked to this User.")

    def on_update(self):
        if not self.issue_id:
            frappe.throw("Issue ID is missing")

        if not self.location_changed:
            return

        if not self.shelf:
            frappe.throw("Please select Re-Shelved Location")

        # Get Issue Request
        issue_doc = frappe.get_doc("Document Issue Request", self.issue_id)

        if not issue_doc.document:
            frappe.throw("No Managed Document linked in Issue Request")

        # Get Managed Document
        managed_doc = frappe.get_doc("Document Registration", issue_doc.document)
        managed_doc.shelf = self.shelf
        managed_doc.rack = self.rack
        managed_doc.status = "Available"
        managed_doc.save(ignore_permissions=True)
        frappe.msgprint("Document updated successfully.")

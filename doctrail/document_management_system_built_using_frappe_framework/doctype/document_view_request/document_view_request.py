# Copyright (c) 2026, sirajpanigrahi@gail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class DocumentViewRequest(Document):
	def after_insert(self):
		self.db_set("document_series", self.name, update_modified=False)
		if self.workflow_state == "Draft":
			current_time = now_datetime()
			frappe.db.set_value(self.doctype, self.name, "draft_time", current_time)

	def on_update(self):
		old_doc = self.get_doc_before_save()

		if not old_doc:
			return

		if old_doc.workflow_state != self.workflow_state:
			current_time = now_datetime()
			if self.workflow_state == "Approved":
					self.db_set("approved_by", frappe.session.user, update_modified=False)
					frappe.db.set_value(self.doctype, self.name, "approved_time", current_time)

			elif self.workflow_state == "Sent For Approval":
				frappe.db.set_value(self.doctype, self.name, "sent_for_approval_time", current_time)


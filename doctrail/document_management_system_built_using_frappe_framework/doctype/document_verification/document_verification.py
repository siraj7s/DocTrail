# Copyright (c) 2026, sirajpanigrahi@gail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class DocumentVerification(Document):
	def after_insert(self):
		if not self.verification_series:
			self.db_set("verification_series", self.name, update_modified=False)

		if self.workflow_state == "Draft":
			current_time = now_datetime()
			frappe.db.set_value(self.doctype, self.name, "draft_time", current_time)

	def on_update(self):
		old_doc = self.get_doc_before_save()
		if not old_doc:
			return

		# Run only when status changes to Verified
		if old_doc.workflow_state != self.workflow_state:
			if self.workflow_state == "Verified":
				for row in self.documents:
					if row.document:
						frappe.db.set_value(
							"Document Registration",
							row.document,
							"condition_at_registration",
							row.physical_condition
						)
						
		if old_doc.workflow_state != self.workflow_state:
			current_time = now_datetime()
			if self.workflow_state == "Verified":
					frappe.db.set_value(self.doctype, self.name, "verified_time", current_time)
					

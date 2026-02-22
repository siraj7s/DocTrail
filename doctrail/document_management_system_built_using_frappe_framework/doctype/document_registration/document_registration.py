# Copyright (c) 2026, siraj.panigrahi@atriina.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DocumentRegistration(Document):
	def validate(self):
		if self.volume_applicable and self.volume_no:
			existing = frappe.db.exists(
				"Document Registration",
				{
					# "document_name": self.document_name.split("-")[0],
					"volume_no": self.volume_no,
					"name": ["!=", self.name]  # exclude current doc
				}
			)

			if existing:
				frappe.throw(
					("Volume No {0} already exists for the document.").format(self.volume_no)
				)
				
	def before_save(self):
		if self.registered_by:
			self.custodian = self.registered_by

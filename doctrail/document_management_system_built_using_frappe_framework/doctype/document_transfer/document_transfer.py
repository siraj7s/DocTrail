# Copyright (c) 2026, siraj.panigrahi@atriina.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class DocumentTransfer(Document):
	def after_insert(self):
		if self.workflow_state == "Draft":
			current_time = now_datetime()
			frappe.db.set_value(self.doctype, self.name, "draft_time", current_time)

		if not self.transfer_series:
			self.db_set("transfer_series", self.name, update_modified=False)
		
	def on_update(self):
		old_doc = self.get_doc_before_save()

		if not old_doc:
			return

		if old_doc.workflow_state != self.workflow_state:
			current_time = now_datetime()
			if self.workflow_state == "Approved":
			# 		for row in self.documents:   # child table fieldname
			# 			if row.document:
			# 				frappe.db.set_value(
			# 					"Document Registration",   # Linked DocType
			# 					row.document,              # Document name
			# 					{
			# 						"group": self.group,
			# 						"shelf": self.shelf,
			# 						"year": self.year
			# 					}
			# 				)
					frappe.db.set_value(self.doctype, self.name, "approved_time", current_time)
					
		if self.workflow_state == "Approved":
			if not self.transfer_to_location:
				frappe.throw("Transfer To Location is required")

			for row in self.documents:
				if not row.document:
					continue

				# Get Document Registratin
				managed_doc = frappe.get_doc("Document Registration", row.document)

				# Update shelf/location
				managed_doc.location = self.transfer_to_location
				managed_doc.save(ignore_permissions=True)

			frappe.msgprint("All documents transferred successfully.")
			self.send_transfer_email()

	def send_transfer_email(self):
		roles = ["Archive Approver", "Archive Librarian"]

		# Get users with these roles
		users = frappe.get_all(
			"Has Role",
			filters={"role": ["in", roles]},
			fields=["parent"]
		)

		user_ids = list(set([u.parent for u in users]))

		# Get user emails
		emails = frappe.get_all(
			"User",
			filters={"name": ["in", user_ids], "enabled": 1},
			fields=["email"]
		)

		email_list = [e.email for e in emails if e.email]

		if not email_list:
			return

		# Site URL
		site_url = frappe.utils.get_url()

		# Document Link
		doc_link = f"{site_url}/app/document-transfer/{self.name}"

		# Document rows
		document_list = ""
		for row in self.documents:
			document_list += f"<li>{row.document}</li>"

		message = f"""
		<h3>Document Transfer Approved</h3>

		<p><b>Transfer ID:</b> {self.name}</p>
		<p><b>From Location:</b> {self.transfer_from_location}</p>
		<p><b>To Location:</b> {self.transfer_to_location}</p>
		<p><b>Transfer Date:</b> {self.date_of_transfer}</p>

		<h4>Transferred Documents:</h4>
		<ul>
			{document_list}
		</ul>

		<p>
			View Transfer:
			<a href="{doc_link}">{doc_link}</a>
		</p>
		"""

		frappe.sendmail(
			recipients=email_list,
			subject=f"Document Transfer Approved - {self.name}",
			message=message
		)
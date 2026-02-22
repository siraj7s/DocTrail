# Copyright (c) 2026, sirajpanigrahi@gail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, getdate, today

class DocumentIssueRequest(Document):
	def validate(self):
		today_date = getdate(today())
		if self.requested_date and getdate(self.requested_date) < today_date:        # Validate Requested Date
			frappe.throw(
				("Requested Date cannot be less than today.")
			)

		if self.expected_return_date and getdate(self.expected_return_date) < today_date:         # Validate Expected Return Date
			frappe.throw(
				("Expected Return Date cannot be less than today.")
			)

	def after_insert(self):
		if self.workflow_state == "Draft":
			current_time = now_datetime()
			frappe.db.set_value(self.doctype, self.name, "draft_time", current_time)

	def on_update(self):
		old_doc = self.get_doc_before_save()

		if not old_doc:
			return

		# Check if workflow_state changed
		if old_doc.workflow_state != self.workflow_state:
			current_time = now_datetime()
			if self.workflow_state == "Requested":
				frappe.db.set_value(self.doctype, self.name, "requested_time", current_time)
				# 🔔 Get all users with role "Archive Requester"
				users = frappe.get_all(
					"Has Role",
					filters={"role": "Archive Approver"},
					fields=["parent"]
				)

				recipients = []
				for user in users:
					email = frappe.db.get_value("User", user.parent, "email")
					if email:
						recipients.append(email)

				recipients = list(set(recipients))
				if recipients:
					frappe.sendmail(
						recipients=recipients,
						subject="New Document Issue Request Raised",
						message=f"""
							Hello,<br><br>
							A new document issue request has been raised.<br><br>
							<b>Request ID:</b> {self.name}<br>
							<b>Document:</b> {self.document}<br>
							<b>Requested By:</b> {self.employee_name}<br><br>
							Please review the request.<br><br>
							Regards,<br>
							Archive System
						""")

			elif self.workflow_state == "Under Review":
				frappe.db.set_value(self.doctype, self.name, "under_review_time", current_time)

			elif self.workflow_state == "Approved":
				self.send_document_email()
				frappe.db.set_value(self.doctype, self.name, "approved_time", current_time)
				# Get users by role
				requester_users = frappe.get_all(
					"Has Role",
					filters={"role": "Archive Requester"},
					pluck="parent"
				)

				librarian_users = frappe.get_all(
					"Has Role",
					filters={"role": "Archive Librarian"},
					pluck="parent"
				)
				user_ids = list(set(requester_users + librarian_users))
				recipients = frappe.get_all(
					"User",
					filters={
						"name": ["in", user_ids],
						"enabled": 1
					},
					pluck="email"
				)

				if recipients:
					frappe.sendmail(
						recipients=recipients,
						subject="Document Request Approved",
						message=f"""
							Hello,<br><br>
							The document request <b>{self.name}</b> has been approved.<br>
							Document: <b>{self.document}</b><br>
							Requested By: <b>{self.owner}</b><br><br>
							Please proceed with the next steps.<br><br>
							Regards,<br>
							Archive System
						"""
					)

			elif self.workflow_state == "Rejected":
				frappe.db.set_value(self.doctype, self.name, "rejected_time", current_time)

			elif self.workflow_state == "Issued":
				frappe.db.set_value(self.doctype, self.name, "issued_time", current_time)

				# Update Custodian to Employee
				if self.document and self.employee_id:
					frappe.db.set_value(
						"Document Registration",
						self.document,
						{
							"custodian": self.employee_id,
							"status": "Issued"
						}
					)

		if old_doc.workflow_state != self.workflow_state and self.workflow_state == "Returned":

			# Prevent duplicate creation
			if not frappe.db.exists("Document Received", {
				"document_issue_request": self.name
			}):
				employee = frappe.db.get_value(
				"Employee",
				{"user_id": frappe.session.user},
				"name"
			)

				if not employee:
					frappe.throw("No Employee linked to this User.")

				new_doc = frappe.new_doc("Document Received")
				new_doc.issue_id = self.name
				new_doc.employee_id = self.employee_id
				new_doc.document = self.document
				new_doc.received_by = employee
				new_doc.insert(ignore_permissions=True)

				# Update Document Registration custodian to Received By
				frappe.db.set_value(
					"Document Registration",
					self.document,
					"custodian",
					new_doc.received_by
				)

	def send_document_email(self):

		# Get document registration record
		doc_reg = frappe.get_doc("Document Registration", self.document)

		# Check confidential
		if doc_reg.is_confidential:
			frappe.throw("Confidential document cannot be shared via email")

		# Check digital file exists
		if not doc_reg.digital_file:
			frappe.throw("No digital file attached to this document")

		# Get requester email
		user_id = frappe.db.get_value("Employee", self.employee_id, "user_id")
		if not user_id:
			frappe.throw("No User linked to this Employee")

		requester_email = frappe.db.get_value("User", user_id, "email")
		if not requester_email:
			frappe.throw("Requester email not found")

		# Get file doc
		file_doc = frappe.get_doc("File", {"file_url": doc_reg.digital_file})

		frappe.sendmail(
			recipients=[requester_email],
			subject=f"Document Approved - {self.document}",
			message=f"""
				Dear {self.employee_name},<br><br>
				Your document request has been approved.<br><br>
				Please find the document attached.<br><br>
				Regards,<br>
				Document Management System
			""",
			attachments=[{
        "fname": file_doc.file_name,
        "fcontent": file_doc.get_content()
    }]
		)
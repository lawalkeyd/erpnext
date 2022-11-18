# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class StudentGroupTimetableDetail(Document):
	def validate_overlap(self):
		"""Validates overlap for Student Group, Instructor, Room"""
		self.validate_time()
		from erpnext.education.utils import validate_timetable_overlap

		# Validate overlapping timetable.
		validate_timetable_overlap(self, "instructor")
		if self.room:
			validate_timetable_overlap(self, "room")

	def validate_time(self):
		"""Validates if Course Start Date is greater than Course End Date"""
		if self.start_time > self.end_time:
			frappe.throw(_(f"Timetable Start Time cannot be greater than Timetable End Time for {self.subject}, start_time {self.start_time}."))
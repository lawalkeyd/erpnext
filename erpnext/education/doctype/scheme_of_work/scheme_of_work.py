# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SchemeOfWork(Document):
	def onload(self):
		"""Load Students for quick view"""
		self.load_lesson_plans()

	def before_save(self):
		for topic in self.topics:
			topic.subject = self.subject

	def load_lesson_plans(self):
		"""Load `lesson plans` from the database"""
		self.lesson_plans = []
		plans = frappe.get_all("Lesson Plan", filters={"scheme_of_work": self.name}, fields=["name", "main_idea"])
		for plan in plans:
			self.append(
				"lesson_plans",
				{
					"lesson_plan": plan.name,
					"main_idea": plan.main_idea,
				},
			)
# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from frappe import _


class CBT(Document):
	def validate(self):
		if self.passing_score > 100:
			frappe.throw(_("Passing Score value should be between 0 and 100"))

	def allowed_attempt(self, enrollment, quiz_name):
		if self.max_attempts == 0:
			return True

		try:
			if (
				len(frappe.get_all("CBT Activity", {"enrollment": enrollment.name, "cbt": quiz_name}))
				>= self.max_attempts
			):
				frappe.msgprint(_("Maximum attempts for this quiz reached!"))
				return False
			else:
				return True
		except Exception as e:
			return False

	def evaluate(self, response_dict):
		questions = [frappe.get_doc("Question", question.question_link) for question in self.questions]
		answers = {q.name: q.get_answer() for q in questions}
		result = {}
		for key in answers:
			try:
				if isinstance(response_dict[key], list):
					is_correct = compare_list_elementwise(response_dict[key], answers[key])
				else:
					is_correct = response_dict[key] == answers[key]
			except Exception as e:
				is_correct = False
			result[key] = is_correct
		score = (sum(result.values()) * 100) / len(answers)
		if score >= self.passing_score:
			status = "Pass"
		else:
			status = "Fail"
		return result, score, status

	def get_questions(self):
		return [frappe.get_doc("Question", question.question_link) for question in self.questions]


def compare_list_elementwise(*args):
	try:
		if all(len(args[0]) == len(_arg) for _arg in args[1:]):
			return all(all([element in (item) for element in args[0]]) for item in args[1:])
		else:
			return False
	except TypeError:
		frappe.throw(_("Compare List function takes on list arguments"))

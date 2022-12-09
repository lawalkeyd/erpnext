# Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
import frappe.defaults
from frappe.model.document import Document
from frappe.utils import date_diff, getdate, add_days, money_in_words
import math

education_keydict = {
	# "key in defaults": "key in Global Defaults"
	"academic_year": "current_academic_year",
	"academic_term": "current_academic_term",
	"validate_batch": "validate_batch",
	"validate_course": "validate_course",
}


num2words = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', \
             6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten', \
            11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen', \
            15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen', \
            19: 'Nineteen', 20: 'Twenty', 30: 'Thirty', 40: 'Forty', \
            50: 'Fifty', 60: 'Sixty', 70: 'Seventy', 80: 'Eighty', \
            90: 'Ninety', 0: 'Zero'}


class EducationSettings(Document):
	def on_update(self):
		"""update defaults"""
		for key in education_keydict:
			frappe.db.set_default(key, self.get(education_keydict[key], ""))

		# clear cache
		frappe.clear_cache()

	def get_defaults(self):
		return frappe.defaults.get_defaults()

	def validate(self):
		from frappe.custom.doctype.property_setter.property_setter import make_property_setter

		if self.get("instructor_created_by") == "Naming Series":
			make_property_setter(
				"Instructor", "naming_series", "hidden", 0, "Check", validate_fields_for_doctype=False
			)
		else:
			make_property_setter(
				"Instructor", "naming_series", "hidden", 1, "Check", validate_fields_for_doctype=False
			)

	@frappe.whitelist()
	def calculate_weeks(self):
		week_list = []
		term = frappe.get_doc('Academic Term', self.current_academic_term)
		weeks = math.ceil(date_diff(term.term_end_date, term.term_start_date) / 7)
		start_date = term.term_start_date
		for name in range(1, weeks + 1):
			start_day_of_week = getdate(start_date).weekday()
			end_date = add_days(start_date, days=6-start_day_of_week)
			if name == weeks:
				week = {"week": num2words[name], "start_date": start_date, "end_date": term.term_end_date, "week_type": "Teaching"}
			else:
				week = {"week": num2words[name], "start_date": start_date, "end_date": end_date, "week_type": "Teaching"}
			week_list.append(week)
			start_date = add_days(end_date, days=1)
		return week_list

def update_website_context(context):
	context["lms_enabled"] = frappe.get_doc("Education Settings").enable_lms

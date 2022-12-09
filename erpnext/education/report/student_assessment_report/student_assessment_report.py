# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from collections import OrderedDict, defaultdict

import frappe
from frappe import _
from erpnext.education.report.course_wise_assessment_report.course_wise_assessment_report import (
	get_formatted_result,
)


def execute(filters=None):
	data, chart, grades = [], [], []
	args = frappe._dict()
	grade_wise_analysis = defaultdict(dict)

	args["academic_year"] = filters.get("academic_year")
	args["assessment_group"] = filters.get("assessment_group")

	args["academic_term"] = filters.get("academic_term")
	args["student"] = filters.get("student")

	if args["assessment_group"] == "All Assessment Groups":
		frappe.throw(_("Please select the assessment group other than 'All Assessment Groups'"))

	returned_values = get_formatted_result(args, get_assessment_criteria=True)
	print(returned_values)
	student_dict = returned_values["student_details"]
	result_dict = returned_values["assessment_result"][filters.get("student")]
	assessment_criteria_dict = returned_values["assessment_criteria"]
	subject_name_list = []

	for subject_name, subject in result_dict.items():
		subject_row = {}
		scrub_subject_name = frappe.scrub(subject_name)
		subject_name_list.append(scrub_subject_name)
		print(subject_name)
		subject_row["Subject"] = subject_name
		assessment_group = filters.get("assessment_group")
		final_grade = subject[assessment_group]["Final Grade"]

		subject_row["Maximum Score"] = final_grade["maximum_score"]
		subject_row["Score"] = final_grade["score"]
		subject_row["Grade"] = final_grade["grade"]

		data.append(subject_row)

	columns = [
		{
			"fieldname": "Subject",
			"label": _("Subject Name"),
			"fieldtype": "Data",
			"width": 160,
		},
		{"fieldname": "Maximum Score", "label": _("Maximum Score"), "fieldtype": "Data", "width": 160},
		{"fieldname": "Score", "label": _("Score"), "fieldtype": "Data", "width": 160},
		{"fieldname": "Grade", "label": _("Grade"), "fieldtype": "Data", "width": 160},
	]
	chart = get_chart_data(data)

	return columns, data, None, chart

def get_chart_data(data):
	datasets = []
	subject_list = []
	value_list = []

	for subject in data:
		subject_name = subject["Subject"]
		subject_list.append(subject_name)
		value_list.append(subject["Score"])

	datasets = [{"values": value_list}]

	return {
		"data": {"labels": subject_list, "datasets": datasets},
		"type": "bar",
	}
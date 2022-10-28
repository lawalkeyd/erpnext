# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from collections import OrderedDict, defaultdict

import frappe
from erpnext.education.report.course_wise_assessment_report.course_wise_assessment_report import (
	get_chart_data,
	get_formatted_result,
	get_column
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

	returned_values = get_formatted_result(args)
	print(returned_values)
	student_dict = returned_values["student_details"]
	result_dict = returned_values["assessment_result"]
	assessment_criteria_dict = returned_values["assessment_criteria"]

	for student in result_dict:
		student_row = {}
		student_row["student"] = student
		student_row["student_name"] = student_dict[student]
		for criteria in assessment_criteria_dict:
			scrub_criteria = frappe.scrub(criteria)
			if criteria in result_dict[student][args.course][args.assessment_group]:
				student_row[scrub_criteria] = result_dict[student][args.course][args.assessment_group][
					criteria
				]["grade"]
				student_row[scrub_criteria + "_score"] = result_dict[student][args.course][
					args.assessment_group
				][criteria]["score"]

				# create the list of possible grades
				if student_row[scrub_criteria] not in grades:
					grades.append(student_row[scrub_criteria])

				# create the dict of for gradewise analysis
				if student_row[scrub_criteria] not in grade_wise_analysis[criteria]:
					grade_wise_analysis[criteria][student_row[scrub_criteria]] = 1
				else:
					grade_wise_analysis[criteria][student_row[scrub_criteria]] += 1
			else:
				student_row[frappe.scrub(criteria)] = ""
				student_row[frappe.scrub(criteria) + "_score"] = ""
		data.append(student_row)

	assessment_criteria_list = [d for d in assessment_criteria_dict]
	columns = get_column(assessment_criteria_dict)
	chart = get_chart_data(grades, assessment_criteria_list, grade_wise_analysis)

	return columns, data, None, chart


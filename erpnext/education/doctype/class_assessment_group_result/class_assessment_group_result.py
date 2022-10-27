# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from pprint import pprint
from itertools import groupby
from operator import itemgetter

import frappe
from frappe.model.document import Document
from frappe import _


from erpnext.education.report.course_wise_assessment_report.course_wise_assessment_report import get_formatted_result

class ClassAssessmentGroupResult(Document):
	@frappe.whitelist()
	def calculate_marks(self):
		students = []
		if not self.assessment_group:
			frappe.throw(_("Mandatory field - Assessment Group"))
		elif not self.program:
			frappe.throw(_("Mandatory field - Class"))
		elif not self.academic_year:
			frappe.throw(_("Mandatory field - Academic Year"))
		else:
			args = frappe._dict()
			args["program"] = self.program
			args["academic_year"] = self.academic_year
			args["assessment_group"] = self.assessment_group
			values = get_formatted_result(args, get_course=True, include_student_group=True)
			student_details = values.get("student_details")
			assessment_result = values.get("assessment_result")
			course_dict = values.get("course_dict")

			student_list = []
			subject_list = []
			subject_dict = {}
			for student in student_details.keys():
				student_info = {}
				student_info["student_name"] = student_details[student]["name"]
				student_info["student_group"] = student_details[student]["student_group"]
				student_info["student"] = student
				total_marks = 0
				attainable_marks = 0
				for course in course_dict:
					if course not in subject_dict:
						subject_dict[course] = {
							"total": 0,
							"students_no": 0
						}
					if self.assessment_group in assessment_result[student][course]:
						student_subject_score = assessment_result[student][course][self.assessment_group][
							"Final Grade"
						]["score"]
						total_marks += student_subject_score
						subject_dict[course]["total"] += student_subject_score
						subject_dict[course]["students_no"] += 1
						attainable_marks += assessment_result[student][course][self.assessment_group][
							"Final Grade"
						]["maximum_score"]
				student_info["total_marks"] = total_marks
				student_info["attainable_marks"] = attainable_marks
				student_list.append(student_info)
			student_list = calculate_student_positions(student_list)
			print(student_list)

			for subject, marks_data in subject_dict.items():
				subject_info = {"subject": subject, "class_average":(marks_data["total"]/marks_data["students_no"])} 
				subject_list.append(subject_info)

		if len(student_list) > 0:
			return student_list, subject_list
		else:
			frappe.throw(_("No students Found"))

	@frappe.whitelist()
	def get_current_academic_info(self):
		settings = frappe.get_doc('Education Settings', ['current_academic_term', 'current_academic_year'])
		return {"academic_year": settings.current_academic_year, "academic_term": settings.current_academic_term}
		

def calculate_student_positions(student_list):
	grades_list = sorted(student_list, key=lambda d: d['total_marks'], reverse=True)
	
	# sort grades into student groups
	new_grades_list = grades_list
	new_grades_list.sort(key=itemgetter("student_group"))
	result = {}
	for student_group, group in groupby(grades_list, key=itemgetter("student_group")):
		result[student_group] = list(group)

	updated_list = []
	for student in grades_list:
		# check if students have the same score
		if len(updated_list) > 1:
			previous_student = updated_list[-1]
			
			# check if student has the same score as previous student
			if  student["total_marks"] == previous_student["total_marks"]:
				student["student_group_position"] = previous_student["student_group_position"]
				student["overall_position"] = previous_student["overall_position"]
				updated_list.append(student)
				continue

		student["student_group_position"] = grades_list.index(student) + 1
		student["overall_position"] = result[student_group].index(student) + 1
		updated_list.append(student)
	
	return updated_list

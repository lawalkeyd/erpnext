from warnings import filters
import frappe
from frappe import _

import erpnext.education.utils as utils

no_cache = 1


def get_context(context):
	try:
		program = frappe.form_dict["program"]
	except KeyError:
		frappe.local.flags.redirect_location = "/lms"
		raise frappe.Redirect

	context.education_settings = frappe.get_single("Education Settings")
	context.program = get_program(program)
	subjects = frappe.db.get_list("Subject", filters={"class": program})
	context.courses = [frappe.get_doc("Subject", subject.name) for subject in subjects]
	context.has_access = utils.allowed_program_access(program)
	progress = get_course_progress(context.courses, context.program)
	context.progress = progress


def get_program(program_name):
	try:
		return frappe.get_doc("Class", program_name)
	except frappe.DoesNotExistError:
		frappe.throw(_("Program {0} does not exist.").format(program_name))


def get_course_progress(courses, program):
	progress = {course.name: utils.get_course_progress(course, program) for course in courses}
	return progress or {}

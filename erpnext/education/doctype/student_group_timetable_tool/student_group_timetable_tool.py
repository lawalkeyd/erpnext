# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import copy
import random
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_datetime

class StudentGroupTimetableTool(Document):
	@frappe.whitelist()
	def get_subjects(self): 
		subjects_list = frappe.db.sql(
				"""select sb.name as subject, si.instructor as instructor from `tabSubject` sb, `tabSubject Instructor` si
				where sb.program=%(class_name)s and sb.name=si.parent""",
				{"class_name": self.program},
				as_dict=1,
			)
		return subjects_list

	@frappe.whitelist()
	def get_default_durations(self):
		duration_doctype = frappe.get_doc("Default Timetable Duration").as_dict()
		duration = duration_doctype.duration
		return duration

	@frappe.whitelist()
	def generate_timetable(self):
		self.validate_mandatory()
		subjects = sorted(self.subjects, key= lambda x: x.is_core, reverse=True)
		timetable_errors = []
		grouped_subjects_to_avoid = []
		durations = self.sort_durations(self.durations)
		timetable = self.create_timetable()
		for idx, subject in enumerate(subjects):
			frappe.publish_realtime(
				"student_group_timetable_progress", {"progress": [idx, len(subjects)]}, user=frappe.session.user
			)
			if subject in grouped_subjects_to_avoid:
				continue
			available_periods = copy.deepcopy(durations)
			allowed_same_day_subject = False
			no_available_periods = False
			for number_of_times in range(subject.number_of_times):
				if no_available_periods: 
					timetable_errors.append([subject.subject, subject.number_of_times - number_of_times])
					break
				while True:
					if len(available_periods) == 0:
						if not allowed_same_day_subject:
							available_periods = copy.deepcopy(durations)
							allowed_same_day_subject = True
						else:
							no_available_periods = True
							break
					random_day = random.choice(list(available_periods.keys()))
					if len(available_periods[random_day]) > 0:
						detail = []
						period = available_periods[random_day][0]
						if subject.group:
							group_subjects = [sub for sub in subjects if sub.group == subject.group]
							detail = [self.add_timetable_detail(sub, random_day, period[0], period[1]) for sub in group_subjects]
							grouped_subjects_to_avoid.extend(group_subjects)
						else:
							detail = self.add_timetable_detail(subject, random_day, period[0], period[1])
						success = self.add_detail_to_timetable(detail, timetable)
						available_periods[random_day].remove(period)
						if success: 
							durations[random_day].remove(period)
							del available_periods[random_day]
							break
					else:
						del available_periods[random_day]
		return dict(
			timetable=timetable,
			timetable_errors=timetable_errors
		)

	def validate_time(self, detail):
		"""Validates if Course Start Date is greater than Course End Date"""
		if get_datetime(detail["start_time"]) > get_datetime(detail["end_time"]):
			frappe.throw(_("Timetable Start Time cannot be greater than Timetable End Time for {}, start_time {}, end_time {}.".format(detail["day"], detail["start_time"], detail["end_time"])))

	def validate_timetable_detail(self, detail, timetable):
		self.validate_time(detail)
		from erpnext.education.utils import validate_timetable_overlap

		# Validate overlapping timetable.
		instructor_overlap = validate_timetable_overlap(detail, "instructor")
		timetable_overlap = validate_timetable_overlap(detail, "parent", timetable)
		room_overlap = False
		if "room" in detail:
			room_overlap = validate_timetable_overlap(detail, "room")

		if instructor_overlap or timetable_overlap or room_overlap:
			return False
		else: 
			return True

	def add_detail_to_timetable(self, detail, timetable):
		if type(detail) == list:
			for det in detail:
				valid = self.validate_timetable_detail(det, timetable)
				if not valid: break	
		else:
			valid = self.validate_timetable_detail(detail, timetable)
		if valid :
			timetable.append("timetable_details", detail)
			timetable.save()
			
		return valid


	def create_timetable(self):
		if frappe.db.exists({'doctype': 'Student Group Timetable', "student_group": self.student_group}):
			timetable = frappe.db.get_value('Student Group Timetable', {"student_group": self.student_group}, 'name')
			frappe.db.delete("Student Group Timetable Detail", {"parent": timetable})
			frappe.db.delete("Student Group Timetable", {"name": timetable})
		timetable = frappe.get_doc({
			'doctype': 'Student Group Timetable',
			'student_group': self.student_group,
			"timetable_details": []
		})
		return timetable.insert()

	def add_timetable_detail(self, subject, day, start_time, end_time):
		"""Makes a new Student Group Timetable Detail.
		:param date: Date on which Course Schedule will be created."""

		timetable_detail = {}
		timetable_detail["subject"] = subject.subject
		timetable_detail["instructor"] = subject.instructor
		timetable_detail["day"] = day
		timetable_detail["start_time"] = start_time
		timetable_detail["end_time"] = end_time
		if subject.room:
			timetable_detail["room"] = subject.room
		return timetable_detail

	def validate_mandatory(self):
		"""Validates all mandatory fields"""

		fields = [
			"student_group",
			"subjects",
			"durations"
		]
		for d in fields:
			if not self.get(d):
				frappe.throw(_("{0} is mandatory").format(self.meta.get_label(d)))

	def sort_durations(self, durations):
		duration_dict = {}
		for duration in durations:
			if duration.day not in duration_dict:
				duration_dict[duration.day] = []
			duration_dict[duration.day].append((duration.start_time, duration.end_time))
		return duration_dict
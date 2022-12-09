// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Student Assessment Report"] = {
	"filters": [
		{
			"fieldname":"academic_year",
			"label": __("Academic Year"),
			"fieldtype": "Link",
			"options": "Academic Year",
			"reqd": 1
		},
		{
			"fieldname":"academic_term",
			"label": __("Academic Term"),
			"fieldtype": "Link",
			"options": "Academic Term"
		},
		{
			"fieldname":"student",
			"label": __("Student"),
			"fieldtype": "Link",
			"options": "Student",
			"reqd": 1
		},
		{
			"fieldname":"assessment_group",
			"label": __("Assessment Group"),
			"fieldtype": "Link",
			"options": "Assessment Group",
			"reqd": 1
		}
	]
};

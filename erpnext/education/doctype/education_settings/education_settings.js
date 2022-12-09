// Copyright (c) 2017, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Education Settings', {
	refresh: function(frm) {

	}
});

frappe.ui.form.on("Education Settings", "calculate_weeks", function(frm) {
	frm.set_value("week",[]);
	frappe.call({
		method: "calculate_weeks",
		doc:frm.doc,
		callback: function(r) {
			if(r.message) {
				frm.set_value("week", r.message);
			}
		}
	});
})

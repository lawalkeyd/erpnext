// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("School Report", {
	setup: function(frm) {
		frm.set_query("topics_taught", function(doc, cdt, cdn) {
			return {
				filters: [
					["Scheme Topic","subject", "=", doc.subject]
				]
			}
		});
	}
});

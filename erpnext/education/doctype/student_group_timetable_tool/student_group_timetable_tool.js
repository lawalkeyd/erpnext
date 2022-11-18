// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student Group Timetable Tool', "refresh", function(frm) {
	frm.disable_save();
	frm.page.set_primary_action(__("Generate Timetable"), function() {
		frappe.call({
			method: "generate_timetable",
			doc:frm.doc,
			callback: function(r) {
				console.log("callback")
				if(!r.message) {
					frappe.throw(__('There were errors generating the Timetable'));
				}
				const { timetable, timetable_errors } = r.message;
				if (timetable) {
					const timetable_error_list = timetable_errors.map(c => `
						<tr>
							<td>${c[0]}</td>
							<td>${c[1]}</td>
						</tr>
					`).join('');
	
					const html = timetable_error_list.length > 0 
					? 
						`
							<h5>View Created Timetable <td><a href="/app/student-group-timetable/${timetable.name}">${timetable.name}</a></td></h5>
							<table class="table table-bordered">
								<caption>${__('Following timetable errors occured')}</caption>
								<thead><tr><th>${__("Subject")}</th><th>${__("Periods")}</th></tr></thead>
								<tbody>
									${timetable_error_list}
								</tbody>
							</table>
						`
					: 
						`<h5>View Created Timetable <td><a href="/app/student-group-timetable/${timetable.name}">${timetable.name}</a></td></h5>`;
	
					frappe.msgprint(html);
				}
			}
		});
	});
	frappe.realtime.on("student_group_timetable_progress", function(data) {
		console.log("progressing")
		if(data.progress) {
			frappe.hide_msgprint(true);
			frappe.show_progress(__("Creating student groups' timetable"), data.progress[0],data.progress[1]);
		}
	})	
});


frappe.ui.form.on("Student Group Timetable Tool", "fetch_subjects", function(frm) {
	frm.set_value("subjects",[]);
	frappe.call({
		method: "get_subjects",
		doc:frm.doc,
		callback: function(r) {
			if(r.message) {
				frm.set_value("subjects", r.message);
			}
		}
	});
}),

frappe.ui.form.on("Student Group Timetable Tool", "fetch_durations", function(frm) {
	frm.set_value("durations",[]);
	frappe.call({
		method: "get_default_durations",
		doc:frm.doc,
		callback: function(r) {
			if(r.message) {
				frm.set_value("durations", r.message);
			}
		}
	});
})



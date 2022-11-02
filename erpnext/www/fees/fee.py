import frappe

import erpnext.education.utils as utils

no_cache = 1


def get_context(context):
    try:
        fee_name = frappe.form_dict["name"]
    except KeyError:
        frappe.local.flags.redirect_location = "/"
        raise frappe.Redirect
    fee = utils.get_student_fee(fee_name)
    if not fee:
        frappe.local.flags.redirect_location = "/"
        raise frappe.Redirect
    
    context.fee = fee
    context.show_sidebar=True


def get_fees():
	return utils.get_guardian_items("Fees") or []
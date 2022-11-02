import frappe

import erpnext.education.utils as utils

no_cache = 1


def get_context(context):
    guardian = utils.get_current_guardian()
    if not guardian:
        frappe.local.flags.redirect_location = "/"
        raise frappe.Redirect
    
    context.fees = get_fees()
    context.show_sidebar=True


def get_fees():
	return utils.get_guardian_items("Fees") or []
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def after_migrate():
	create_custom_fields(get_custom_fields())
 
	# Remove Custom Fields
	set_poi_einkaufspreis_to_purchase_price()
	set_quoi_einkaufspreis_to_purchase_price()

def before_uninstall():
	delete_custom_fields(get_custom_fields())


def delete_custom_fields(custom_fields):
	for doctype, fields in custom_fields.items():
		for field in fields:
			custom_field_name = frappe.db.get_value(
				"Custom Field", dict(dt=doctype, fieldname=field.get("fieldname"))
			)
			if custom_field_name:
				frappe.delete_doc("Custom Field", custom_field_name)

		frappe.clear_cache(doctype=doctype)


def set_poi_einkaufspreis_to_purchase_price():
	if frappe.db.exists("Custom Field", "Purchase Order Item-einkaufspreis"):
		# First set the value of wrong `reoccurring_maintenance_amount` field into `reoccurring_maintenance_amount`
		frappe.db.sql("update `tabPurchase Order Item` set `purchase_price` = `einkaufspreis`")
		# Now removing the field
		frappe.delete_doc("Custom Field", "Purchase Order Item-einkaufspreis", force=1)

def set_quoi_einkaufspreis_to_purchase_price():
	if frappe.db.exists("Custom Field", "Quotation Item-einkaufspreis"):
		# First set the value of wrong `reoccurring_maintenance_amount` field into `reoccurring_maintenance_amount`
		frappe.db.sql("update `tabQuotation Item` set `purchase_price` = `einkaufspreis`")
		# Now removing the field and its section
		frappe.delete_doc("Custom Field", "Quotation Item-einkauf", force=1)
		frappe.delete_doc("Custom Field", "Quotation Item-einkaufspreis", force=1)


def get_custom_fields():
	custom_fields_customer = [
		{
			"label": "SimpaTec",
			"fieldname": "simpatec_section",
			"fieldtype": "Section Break",
		},
		{
			"label": "Is Supplier",
			"fieldname": "is_supplier",
			"fieldtype": "Check",
			"insert_after": "simpatec_section"
		},
		{
			"label": "Ist Vertriebspartner",
			"fieldname": "ist_vertriebspartner",
			"fieldtype": "Check",
			"insert_after": "is_supplier"
		},
		{
			"label": "Vertriebs_partner",
			"fieldname": "vertriebs_partner",
			"fieldtype": "Link",
			"options": "Customer",
			"insert_after": "ist_vertriebspartner"
		},
		{
			"label": "Supplier",
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier",
			"insert_after": "vertriebs_partner"
		},
		{
			"label": "Supplier Number",
			"fieldname": "supplier_number",
			"fieldtype": "Data",
			"insert_after": "supplier"
		},
		{
			"label": "Additional Information",
			"fieldname": "additional_information",
			"fieldtype": "Column Break",
			"insert_after": "supplier_number"
		},
		{
			"label": "Mutter",
			"fieldname": "mutter",
			"fieldtype": "Link",
			"options": "Customer",
			"insert_after": "additional_information"
		},
		{
			"label": "Rechnungsversand",
			"fieldname": "rechnungsversand",
			"fieldtype": "Select",
			"options": "\nE-Mail\npostalisch",
			"insert_after": "mutter"	
		},
		{
			"label": "Zahlungsschwierigkeiten",
			"fieldname": "zahlungsschwierigkeiten",
			"fieldtype": "Select",
			"options": 'keine\nJa "Achtung"\n!!! STOPP keine Verkäufe mehr !!!',
			"insert_after": "rechnungsversand"	
		},
		{
			"label": "Customer since",
			"fieldname": "customer_since",
			"fieldtype": "Date",
			"insert_after": "zahlungsschwierigkeiten"	
		}
	]


	custom_fields_so = [
		{
			"label": "SimpaTec",
			"fieldname": "simpatec_section",
			"fieldtype": "Section Break",
		},	
		{
			"label": "Sales Order Type",
			"fieldname": "sales_order_type",
			"fieldtype": "Select",
			"options": "\nFirst Sale\nFollow-Up Sale\nReoccuring Maintenance\nRTO\nSubscription Annual\nInternal Clearance\nOther",
			"default": "",
			"insert_after": "simpatec_section"
		},
		{
			"label": "Eligable for Clearance",
			"fieldname": "eligable_for_clearance",
			"fieldtype": "Check",
			"allow_on_submit": 1,
			"depends_on": "eval:doc.sales_order_type != \"Internal Clearance\" && doc.sales_order_type != \"\"",
			"insert_after": "sales_order_type",
		},
		{
			"label": "Item Group",
			"fieldname": "item_group",
			"fieldtype": "Link",
			"options": "Item Group",
			"insert_after": "eligable_for_clearance"
		},
		{
			"label": "Quotation Label",
			"fieldname": "quotation_label",
			"fieldtype": "Link",
			"options": "Angebotsvorlage",
			"insert_after": "item_group"
		},
		{
			"label": "Performance Period Start",
			"fieldname": "performance_period_start",
			"fieldtype": "Date",
			"description": "Muss gefüllt werden wenn Wartungspositionen in Auftrag gehen.",
			"insert_after": "quotation_label",
		},
		{
			"fieldname": "column_break_fdgxg",
			"fieldtype": "Column Break",
			"insert_after": "performance_period_start",
		},
		{
			"label": "UID",
			"fieldname": "uid",
			"fieldtype": "Data",
			"insert_after": "column_break_fdgxg"
		},
		{
			"label": "Customer Subsidiary",
			"fieldname": "customer_subsidiary",
			"fieldtype": "Link",
			"options": "Customer Subsidiary",
			"reqd":1,
			"insert_after": "uid"
		},
		{
			"label": "Performance Period End",
			"fieldname": "performance_period_end",
			"fieldtype": "Date",
			"description": "Muss gefüllt werden wenn Wartungspositionen in Auftrag gehen.",
			"insert_after": "customer_subsidiary",
		},
		{
			"label": "Assigned to",
			"fieldname": "assigned_to",
			"fieldtype": "Link",
			"options": "User",
			"fetch_from": "customer_subsidiary.assigned_to",
			"fetch_if_empty":1,
			"insert_after": "performance_period_end"
		},
		{
			"label": "Ihr Ansprechpartner",
			"fieldname": "ihr_ansprechpartner",
			"fieldtype": "Link",
			"options": "Employee",
			"reqd":1,
			"insert_after": "assigned_to"
		},
		{
			"label": "Internal Clearance",
			"fieldname": "internal_clearance",
			"fieldtype": "Section Break",
			"depends_on": "eval:doc.sales_order_type == \"Internal Clearance\" || doc.eligable_for_clearance == 1 ",
			"insert_after": "ihr_ansprechpartner",
		},
		{
			"label": "Sales Order Clearances",
			"fieldname": "sales_order_clearances",
			"fieldtype": "Table",
			"options": "Sales Order Clearances",
			"depends_on": "eval:doc.sales_order_type == \"Internal Clearance\"",
			"insert_after": "internal_clearance"
		},
		{
			"label": "Internal Clearance Details",
			"fieldname": "internal_clearance_details",
			"fieldtype": "Link",
			"options": "Internal Clearance Details",
			"allow_on_submit": 1,
			"depends_on": "eval:doc.sales_order_type != \"Internal Clearance\" && doc.eligable_for_clearance == 1 && doc.sales_order_type != \"\"",
			"insert_after": "sales_order_clearances",
		},
		{
			"label": "Purchase Order Total",
			"fieldname": "po_total",
			"fieldtype": "Currency",
			"read_only": 1,
			"no_copy": 1,
			"allow_on_submit": 1,
			"depends_on": "eval:doc.sales_order_type != \"Internal Clearance\" && doc.eligable_for_clearance == 1 && doc.sales_order_type != \"\"",
			"insert_after": "internal_clearance_details",
		},
		{
			"label": "Sales Order Margin",
			"fieldname": "so_margin",
			"fieldtype": "Currency",
			"read_only": 1,
			"no_copy": 1,
			"allow_on_submit": 1,
			"depends_on": "eval:doc.sales_order_type != \"Internal Clearance\" && doc.eligable_for_clearance == 1 && doc.sales_order_type != \"\"",
			"insert_after": "po_total",
		},
		{
			"label": "Sales Order Margin Percentage",
			"fieldname": "so_margin_percent",
			"fieldtype": "Percent",
			"read_only": 1,
			"no_copy": 1,
			"allow_on_submit": 1,
			"depends_on": "eval:doc.sales_order_type != \"Internal Clearance\" && doc.eligable_for_clearance == 1 && doc.sales_order_type != \"\"",
			"insert_after": "so_margin",
		},
		{
			"label": "Clearance Amount",
			"fieldname": "clearance_amount",
			"fieldtype": "Currency",
			"description": "Clearance Amount = ((Sales Order Net Amount) - (Purchase Order Net Amount)) * (Clearance Rate)",
			"read_only": 1,
			"no_copy": 1,
			"allow_on_submit": 1,
			"depends_on": "eval:doc.sales_order_type != \"Internal Clearance\" && doc.eligable_for_clearance == 1 && doc.sales_order_type != \"\"",
			"insert_after": "so_margin_percent",
		},
		{
			"fieldname": "column_break_jvteb",
			"fieldtype": "Column Break",
			"insert_after": "clearance_amount",
		},
		{
			"label": "Clear By",
			"fieldname": "clear_by",
			"fieldtype": "Link",
			"options": "Company",
			"allow_on_submit": 1,
			"depends_on": "eval:doc.sales_order_type != \"Internal Clearance\" && doc.eligable_for_clearance == 1 && doc.sales_order_type != \"\"",
			"insert_after": "column_break_jvteb",
		},
		{
			"label": "Clearance Status",
			"fieldname": "clearance_status",
			"fieldtype": "Select",
			"options": "\nCleared\nNot Cleared\n",
			"default": "Not Cleared",
			"read_only": 1,
			"depends_on": "eval:doc.sales_order_type != \"Internal Clearance\" && doc.eligable_for_clearance == 1 && doc.sales_order_type != \"\"",
			"insert_after": "clear_by",
		},
		{
			"label": "Software Maintenance",
			"fieldname": "software_maintenance",
			"fieldtype": "Link",
			"options": "Software Maintenance",
			"insert_after": "accounting_dimensions_section",
		},
	]

	custom_fields_soi = [
		{
			"label": "SimpaTec",
			"fieldname": "simpatec_section",
			"fieldtype": "Section Break",
			"insert_after": ""
		},	
		{
			"label": "Item Type",
			"fieldname": "item_type",
			"fieldtype": "Data",
			"fetch_from": "item_code.item_type",
			"read_only": 1,
			"fetch_if_empty": 1,
			"insert_after": "simpatec_section",
		
		},
		{
			"fieldname": "column_break_vh0vp",
			"fieldtype": "Column Break",
			"insert_after": "item_type",
		},
		{
			"label": "Reoccurring Maintenance Amount",
			"fieldname": "reoccurring_maintenance_amount",
			"fieldtype": "Currency",
			"description": "The grand total of the reoccurring maintenance cost",
			"depends_on": "eval: doc.item_type == \"Maintenance Item\"",
			"insert_after": "column_break_vh0vp"
		},
		{
			"fieldname": "section_break_kiny4",
			"fieldtype": "Section Break",
			"insert_after": "reoccurring_maintenance_amount"
		},
		{
			"label": "Item Language",
			"fieldname": "item_language",
			"fieldtype": "Link",
			"options": "Language",
			"insert_after": "col_break1",
		},
		{
			"label": "Start Date",
			"fieldname": "start_date",
			"fieldtype": "Date",
			"insert_after": "item_language",
		},
		{
			"label": "End Date",
			"fieldname": "end_date",
			"fieldtype": "Date",
			"insert_after": "start_date",
		},
		{
			"label": "Item Name EN",
			"fieldname": "item_name_en",
			"fieldtype": "Data",
			"fetch_from": "item_code.in_en",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'en'",
			"insert_after": "item_name",
		},
		{
			"label": "Item Name DE",
			"fieldname": "item_name_de",
			"fieldtype": "Data",
			"fetch_from": "item_code.in_de",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'de'",
			"insert_after": "item_name_en",
		},
		{
			"label": "Item Name FR",
			"fieldname": "item_name_fr",
			"fieldtype": "Data",
			"fetch_from": "item_code.in_fr",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'fr'",
			"insert_after": "item_name_de",
		},
  
		# NEW ITEM DESCRIPTION FIELDS
		{
			"label": "Item Description EN",
			"fieldname": "item_description_en",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.id_en",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'en'",
			"insert_after": "description",
		},
		{
			"label": "Item Description DE",
			"fieldname": "item_description_de",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.id_de",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'de'",
			"insert_after": "item_description_en",
		},
		{
			"label": "Item Description FR",
			"fieldname": "item_description_fr",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.in_fr",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'fr'",
			"insert_after": "item_description_de",
		},
		# END NEW ITEM DESCRIPTION FIELDS
  
		{
			"label": "Item Description EN",
			"fieldname": "id_en",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.id_en",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'en'",
   			"hidden": 1,
			"insert_after": "description",
		},
		{
			"label": "Item Description DE",
			"fieldname": "id_de",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.id_de",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'de'",
   			"hidden": 1,
			"insert_after": "id_en",
		},
		{
			"label": "Item Description FR",
			"fieldname": "id_fr",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.in_fr",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'fr'",
   			"hidden": 1,
			"insert_after": "id_de",
		},
		{
			"label": "Purchase",
			"fieldname": "purchase_section",
			"insert_after": "transaction_date",
			"fieldtype": "Section Break",
		},
  		{
			"label": "Purchase Price",
			"fieldname": "purchase_price",
			"insert_after": "purchase_section",
			"fieldtype": "Currency",
			"allow_on_submit": 1,
		}
	]

	custom_fields_item = [
		{
			"label": "Translation",
			"fieldname": "translation",
			"fieldtype": "Section Break",
			"insert_after": "image",
		},
		{
			"label": "Item Name EN",
			"fieldname": "in_en",
			"fieldtype": "Data",
			"insert_after": "translation",
		},
		{
			"label": "Item Description EN",
			"fieldname": "id_en",
			"fieldtype": "Text Editor",
			"insert_after": "in_en",
		},
		{
			"label": "Item Name DE",
			"fieldname": "in_de",
			"fieldtype": "Data",
			"insert_after": "id_en",
		},
		{
			"label": "Item Description DE",
			"fieldname": "id_de",
			"fieldtype": "Text Editor",
			"insert_after": "in_de",
		},
		{
			"label": "Item Name FR",
			"fieldname": "in_fr",
			"fieldtype": "Data",
			"insert_after": "id_de",
		},
		{
			"label": "Item Description FR",
			"fieldname": "id_fr",
			"fieldtype": "Text Editor",
			"insert_after": "in_fr",
		},
		{
			"label": "Item Type",
			"fieldname": "item_type",
			"fieldtype": "Select",
			"options":  "\nMaintenance Item\nInflation Item",
			"insert_after": "simpatec",
		},
	]

	custom_fields_si = [
		{
			"label": "Software Maintenance",
			"fieldname": "software_maintenance",
			"fieldtype": "Link",
			"options": "Software Maintenance",
			"insert_after": "accounting_dimensions_section",
		},
  		{
			"label": "Customer Subsidiary",
			"fieldname": "customer_subsidiary",
			"fieldtype": "Link",
			"options": "Customer Subsidiary",
			"insert_after": "customer_name",
		},
	]

	custom_fields_po = [
		{
			"label": "Software Maintenance",
			"fieldname": "software_maintenance",
			"fieldtype": "Link",
			"options": "Software Maintenance",
			"insert_after": "accounting_dimensions_section",
		},
	]

	custom_fields_pi = [
		{
			"label": "Software Maintenance",
			"fieldname": "software_maintenance",
			"fieldtype": "Link",
			"options": "Software Maintenance",
			"insert_after": "accounting_dimensions_section",
		},
	]

	custom_fields_poi = [
		{
			"label": "SimpaTec",
			"fieldname": "simpatec_sec_br",
			"fieldtype": "Section Break",
			"insert_after": "",
		},
		{
			"label": "Print Options",
			"fieldname": "print_options",
			"fieldtype": "Select",
			"options": "\nItem Name\nItem Name and Description\nDescription\nHide Both",
			"default": "Item Name and Description",
			"insert_after": "simpatec_sec_br",
		},
		{
			"label": "",
			"fieldname": "sec_br_",
			"fieldtype": "Section Break",
			"insert_after": "print_options",
		},
		{
			"label": "Item Language",
			"fieldname": "item_language",
			"fieldtype": "Link",
			"options": "Language",
			"depends_on": "eval: [\"Item Name\",\"Item Name and Description\", \"Description\"].includes(doc.print_options)",
			"insert_after": "column_break_4",
		},
		{
			"label": "Item Name EN",
			"fieldname": "item_name_en",
			"fieldtype": "Data",
			"fetch_from": "item_code.in_en",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'en' && [\"Item Name\",\"Item Name and Description\"].includes(doc.print_options)",
			"insert_after": "item_name",
		},
		{
			"label": "Item Name DE",
			"fieldname": "item_name_de",
			"fieldtype": "Data",
			"fetch_from": "item_code.in_de",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'de' && [\"Item Name\",\"Item Name and Description\"].includes(doc.print_options)",
			"insert_after": "item_name_en",
		},
		{
			"label": "Item Name FR",
			"fieldname": "item_name_fr",
			"fieldtype": "Data",
			"fetch_from": "item_code.in_fr",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'fr' && [\"Item Name\",\"Item Name and Description\"].includes(doc.print_options)",
			"insert_after": "item_name_de",
		},
		{
			"label": "Item Description EN",
			"fieldname": "item_description_en",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.id_en",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'en' && [\"Item Name and Description\", \"Description\"].includes(doc.print_options)",
			"insert_after": "description",
		},
		{
			"label": "Item Description DE",
			"fieldname": "item_description_de",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.id_de",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'de' && [\"Item Name and Description\", \"Description\"].includes(doc.print_options)",
			"insert_after": "item_description_en",
		},
		{
			"label": "Item Description FR",
			"fieldname": "item_description_fr",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.in_fr",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'fr' && [\"Item Name and Description\", \"Description\"].includes(doc.print_options)",
			"insert_after": "item_description_de",
		},
		{
			"label": "Purchase Price",
			"fieldname": "purchase_price",
			"fieldtype": "Currency",
			"description": "Preis welcher schon beim erstellen des Angebots bekannt war",
			"insert_after": "sec_break1",
		},

	]
 	
	custom_fields_quo = [
     	{
			"label": "Customer Subsidiary",
			"fieldname": "customer_subsidiary",
			"fieldtype": "Link",
			"options": "Customer Subsidiary",
			"insert_after": "party_name",
		},
		{
			"label": "SimpaTec",
			"fieldname": "simpatec_section",
			"fieldtype": "Section Break",
		},	
		{
			"label": "Sales Order Type",
			"fieldname": "sales_order_type",
			"fieldtype": "Select",
			"options": "\nFirst Sale\nFollow-Up Sale\nReoccuring Maintenance\nRTO\nSubscription Annual\nInternal Clearance\nOther",
			"default": "",
			"insert_after": "simpatec_section"
		},
		{
			"label": "Item Group",
			"fieldname": "item_group",
			"fieldtype": "Link",
			"options": "Item Group",
			"insert_after": "sales_order_type"
		},
		{
			"label": "Quotation Label",
			"fieldname": "quotation_label",
			"fieldtype": "Link",
			"options": "Angebotsvorlage",
			"insert_after": "item_group"
		},
		{
			"label": "Performance Period Start",
			"fieldname": "performance_period_start",
			"fieldtype": "Date",
			"description": "Muss gefüllt werden wenn Wartungspositionen in Auftrag gehen.",
			"insert_after": "quotation_label",
		},
		{
			"fieldname": "column_break_fdgxg",
			"fieldtype": "Column Break",
			"insert_after": "performance_period_start",
		},
  		{
			"label": "Software Maintenance",
			"fieldname": "software_maintenance",
			"fieldtype": "Link",
			"options": "Software Maintenance",
			"insert_after": "column_break_fdgxg",
		},
		{
			"label": "Performance Period End",
			"fieldname": "performance_period_end",
			"fieldtype": "Date",
			"description": "Muss gefüllt werden wenn Wartungspositionen in Auftrag gehen.",
			"insert_after": "software_maintenance",
		},
  		{
			"label": "Assigned to",
			"fieldname": "assigned_to",
			"fieldtype": "Link",
			"options": "User",
			"fetch_from": "customer_subsidiary.assigned_to",
			"fetch_if_empty":1,
			"insert_after": "performance_period_end"
		},
		{
			"label": "Ihr Ansprechpartner",
			"fieldname": "ihr_ansprechpartner",
			"fieldtype": "Link",
			"options": "Employee",
			"reqd":1,
			"insert_after": "assigned_to"
		},
		
	]
 
	custom_fields_quoi = [
		{
			"label": "SimpaTec",
			"fieldname": "simpatec_section",
			"fieldtype": "Section Break",
			"insert_after": ""
		},	
		{
			"label": "Item Type",
			"fieldname": "item_type",
			"fieldtype": "Data",
			"fetch_from": "item_code.item_type",
			"read_only": 1,
			"fetch_if_empty": 1,
			"insert_after": "simpatec_section",
		},
		{
			"fieldname": "column_break_vh0vp",
			"fieldtype": "Column Break",
			"insert_after": "item_type",
		},
		{
			"label": "Reoccurring Maintenance Amount",
			"fieldname": "reoccurring_maintenance_amount",
			"fieldtype": "Currency",
			"description": "The grand total of the reoccurring maintenance cost",
			"depends_on": "eval: doc.item_type == \"Maintenance Item\"",
			"insert_after": "column_break_vh0vp"
		},
  		{
			"fieldname": "section_break_kiny4",
			"fieldtype": "Section Break",
			"insert_after": "reoccurring_maintenance_amount"
		},
		{
			"label": "Item Language",
			"fieldname": "item_language",
			"fieldtype": "Link",
			"options": "Language",
			"insert_after": "col_break1",
		},
  		{
			"label": "Start Date",
			"fieldname": "start_date",
			"fieldtype": "Date",
			"insert_after": "item_language",
		},
		{
			"label": "End Date",
			"fieldname": "end_date",
			"fieldtype": "Date",
			"insert_after": "start_date",
		},
		{
			"label": "Item Name EN",
			"fieldname": "item_name_en",
			"fieldtype": "Data",
			"fetch_from": "item_code.in_en",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'en'",
			"insert_after": "item_name",
		},
		{
			"label": "Item Name DE",
			"fieldname": "item_name_de",
			"fieldtype": "Data",
			"fetch_from": "item_code.in_de",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'de'",
			"insert_after": "item_name_en",
		},
		{
			"label": "Item Name FR",
			"fieldname": "item_name_fr",
			"fieldtype": "Data",
			"fetch_from": "item_code.in_fr",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'fr'",
			"insert_after": "item_name_de",
		},
		# NEW ITEM DESCRIPTION FIELDS
		{
			"label": "Item Description EN",
			"fieldname": "item_description_en",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.id_en",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'en'",
			"insert_after": "description",
		},
		{
			"label": "Item Description DE",
			"fieldname": "item_description_de",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.id_de",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'de'",
			"insert_after": "item_description_en",
		},
		{
			"label": "Item Description FR",
			"fieldname": "item_description_fr",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.in_fr",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'fr'",
			"insert_after": "item_description_de",
		},
		# END NEW ITEM DESCRIPTION FIELDS
		{
			"label": "Item Description EN",
			"fieldname": "id_en",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.id_en",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'en'",
   			"hidden": 1,
			"insert_after": "description",
		},
		{
			"label": "Item Description DE",
			"fieldname": "id_de",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.id_de",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'de'",
   			"hidden": 1,
			"insert_after": "id_en",
		},
		{
			"label": "Item Description FR",
			"fieldname": "id_fr",
			"fieldtype": "Text Editor",
			"fetch_from": "item_code.in_fr",
			"fetch_if_empty": 1,
			"depends_on": "eval:doc.item_language == 'fr'",
   			"hidden": 1,
			"insert_after": "id_de",
		},
		{
			"label": "Purchase",
			"fieldname": "purchase_section",
			"fieldtype": "Section Break",
			"insert_after": "page_break",
		},
  		{
			"label": "Purchase Price",
			"fieldname": "purchase_price",
			"fieldtype": "Currency",
			"allow_on_submit": 1,
			"insert_after": "purchase_section",
		}
	]


	return {
		"Customer": custom_fields_customer,
		"Sales Order": custom_fields_so,
		"Sales Order Item": custom_fields_soi,
		"Item": custom_fields_item,
		"Sales Invoice": custom_fields_si,
		"Purchase Invoice": custom_fields_pi,
		"Purchase Order": custom_fields_po,
		"Purchase Order Item": custom_fields_poi,
		"Quotation": custom_fields_quo,
		"Quotation Item": custom_fields_quoi
	}

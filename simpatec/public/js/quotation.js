frappe.ui.form.on('Quotation', {
	refresh: function(frm) {
		frm.toggle_reqd("item_group", 1);
		frm.toggle_reqd("quotation_label", 1);
		
        function addClearIconToField(field) {
            if (!field.$clear_icon_appended) {
                field.$clear_icon_appended = true;

				var $clearIcon = $('<span id="xsimpactggleicon" class="clear-icon" style="cursor: pointer; position: absolute; right: 35px; top: 50%; transform: translateY(-50%); font-size: 15px; width: 18px; height: 18px; line-height: 18px; text-align: center; border-radius: 50%;  color: #1C2126;"><svg class="icon "> <use href="#icon-filter-x"></use> </svg> </span>');
                field.$input.parent().css('position', 'relative'); 
                field.$input.css('position', 'relative'); 
                field.$input.after($clearIcon);

                $clearIcon.on('click', function() {
					let qd = cur_frm.fields_dict["anschreiben_vorlage"].get_query();
					var x = document.getElementById("xsimpactggleicon").children[0];
					if (!(qd == undefined) && qd.filters.language === frm.doc.language){
						x.innerHTML = '<use href="#icon-filter"></use>';
						frm.set_query("anschreiben_vorlage", () => {
							let filters = {};
							/* return {
								filters: filters
							} */
						});
					}
					else{
						x.innerHTML = '<use href="#icon-filter-x"></use>';
						frm.set_query("anschreiben_vorlage", () => {
							let filters = {};
							if (frm.doc.language) filters["language"] = frm.doc.language;
							return {
								filters: filters
							}
						});

					}
                    					
					frm.set_value(field.df.fieldname, '');
                });
            }
        }
		
		if(frm.doc.docstatus == 0){
			$.each(frm.fields_dict, function(fieldname, field) {
				
				if (fieldname == 'anschreiben_vorlage') {
					addClearIconToField(field);
				}
			});
			
			// GET ITEMS FROM 
			frm.add_custom_button(__('Quotation'), function () {
				erpnext.utils.map_current_doc({
					method: "simpatec.events.quotation.make_quotation",
					source_doctype: "Quotation",
					target: frm,
					size: "extra-large",
					setters: [
						{
							label: "Customer",
							fieldname: "party_name",
							fieldtype: "Link",
							options: "Customer",
							default: frm.doc.party_name || undefined
						},
						{
							label: "Quotation Label",
							fieldname: "quotation_label",
							fieldtype: "Link",
							options: "Angebotsvorlage",
							default: frm.doc.quotation_label || undefined
						},
						{
							label: "Item Group",
							fieldname: "item_group",
							fieldtype: "Link",
							options: "Item Group",
							default: frm.doc.item_group || undefined
						},

					],
					get_query_filters: {
						company: frm.doc.company,
						docstatus: 1,
						status: ["!=", "Lost"]
					}
				})
			}, __("Get Items From"));

			// Add Conditional Mandatory On Start/End Dates
			frm.events.start_end_date_conditional_mandatory(frm)
		}
    },
	setup: function(frm){
		frm.set_query("anschreiben_vorlage", () => {
			let filters = {};
			if (frm.doc.language) filters["language"] = frm.doc.language;
			return {
				filters: filters
			}
		});
		frm.copy_from_previous_row = function(parentfield, current_row, fieldnames){
			

			var data = frm.doc[parentfield];
			let idx = data.indexOf(current_row);
			if (data.length === 1 || data[0] === current_row) return;
			
			if (typeof fieldnames === "string") {
				fieldnames = [fieldnames];
			}			
			
			$.each(fieldnames, function (i, fieldname) {
				frappe.model.set_value(
					current_row.doctype,
					current_row.name,
					fieldname,
					data[idx - 1][fieldname]
				);
			});
		},
		frm.auto_fill_all_empty_rows = function(doc, dt, dn, table_fieldname, fieldname) {
			var d = locals[dt][dn];
			if(d[fieldname]){
				var cl = doc[table_fieldname] || [];
				for(var i = 0; i < cl.length; i++) {
					if(cl[i][fieldname]) cl[i][fieldname] = d[fieldname];
				}
			}
			refresh_field(table_fieldname);
		},
		frm.occurence_len = function(arr, element){
			
			return arr.filter(
				(ele) => ele.item_language == element
			).length;
		}

		frm.set_query("customer_subsidiary", () => {
			return {
				filters: {
					customer: frm.doc.party_name
				}
			}
		});
	},

	customer_subsidiary: function(frm){
		frappe.call({
			'method': 'frappe.client.get',
			args: {
				doctype: 'Customer Subsidiary',
				name: frm.doc.customer_subsidiary
			},
			callback: function (data) {
				let values = {
					'payment_terms_template': data.message.payment_term,
				};
				if(is_null(frm.doc.payment_terms_template)){
					frm.set_value(values);
				}
			}
		});
	},

	sales_order_type: function(frm){
		// Add Conditional Mandatory On Start/End Dates
		frm.events.start_end_date_conditional_mandatory(frm)
	},

	start_end_date_conditional_mandatory: function (frm) {
		if (["Reoccuring Maintenance"].includes(frm.doc.sales_order_type)) {
			frm.toggle_reqd("performance_period_start", 1)
			frm.toggle_reqd("performance_period_end", 1)
		}
		else {
			frm.toggle_reqd("performance_period_start", 0)
			frm.toggle_reqd("performance_period_end", 0)
		}
	},
});

frappe.ui.form.on('Quotation Item',{
	//
	item_name: function(frm, cdt, cdn){

		var data = frm.doc.items;
		var row = locals[cdt][cdn];
		if (data.length === 1 || data[0] === row) {
			if (frm.doc.language){
				row.item_language = frm.doc.language;
				refresh_field("item_language", cdn, "items");
			}
			
		} else {
			frm.copy_from_previous_row("items", row, ["item_language"]);
		}	
	},

	item_language: function(frm, cdt, cdn){
		
		var data = frm.doc.items;
		
		var row = locals[cdt][cdn];
		if(!(frm.doc.language=== row.item_language)){			
			let row_occurence = frm.occurence_len(data, row.item_language);
			if (row_occurence < data.length && !cur_dialog){
			
				frappe.confirm("💬"+__("  The language <b>{0}</b> in the just edited row is different to the others. Should <b>{0}</b> apply to all rows?", [ row.item_language]),
				()=>{
					frm.auto_fill_all_empty_rows(frm.doc, cdt, cdn, "items", "item_language");
				}, ()=>{
					//cancel
				})
			}
			//
		}
		else if (frm.doc.language=== row.item_language){
			
			let row_occurence = frm.occurence_len(data, row.item_language);
			if (row_occurence < data.length && !cur_dialog){
				//				
				frappe.confirm("💬"+__("    The language <b>'{0}'</b> in the just edited row is different to the others. Should <b>'{0}'</b> apply to all rows?", [ row.item_language]),
					()=>{
							frm.auto_fill_all_empty_rows(frm.doc, cdt, cdn, "items", "item_language");
						}, 
					()=>{
						//cancel
					}
				)
			}
		}
		
		
	},
	
});
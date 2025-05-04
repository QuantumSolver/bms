frappe.pages["ftraxx"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("ftraxx"),
		single_column: true,
	});
};

frappe.pages["ftraxx"].on_page_show = function (wrapper) {
	load_desk_page(wrapper);
};

function load_desk_page(wrapper) {
	let $parent = $(wrapper).find(".layout-main-section");
	$parent.empty();

	frappe.require("ftraxx.bundle.js").then(() => {
		frappe.ftraxx = new frappe.ui.Ftraxx({
			wrapper: $parent,
			page: wrapper.page,
		});
	});
}
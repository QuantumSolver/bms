frappe.pages["ftraxx-1"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("ftraxx"),
		single_column: true,
	});
};

frappe.pages["ftraxx-1"].on_page_show = function (wrapper) {
	load_desk_page(wrapper);
};

function load_desk_page(wrapper) {
	let $parent = $(wrapper).find(".layout-main-section");
	$parent.empty();

	frappe.require("ftraxx_1.bundle.js").then(() => {
		frappe.ftraxx_1 = new frappe.ui.Ftraxx1({
			wrapper: $parent,
			page: wrapper.page,
		});
	});
}
export function createToast(message, type = "success") {
    frappe.utils.play_sound("click");
    frappe.show_alert({
      message: message,
      indicator: type === "success" ? "green" : "red"
    }, 3);
  }
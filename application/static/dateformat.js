moment.locale(get_locale());
function js_date_format() {
    var fmts = document.querySelectorAll(".js-date-format");
    for (var i = 0; i < fmts.length; ++i) {
        var e = fmts[i];
        if (e.hasAttribute("data-timestamp")) {
            var old = +(e.getAttribute("data-timestamp"));
            e.textContent = moment(old, "X").fromNow() + (e.getAttribute("data-edited") == "1" ? "*" : "");
        }
    }
}
add_reload_listener(js_date_format);
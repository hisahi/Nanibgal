var reload_listeners = [];
function add_reload_listener(func) {
    reload_listeners.push(func);
}
function do_reload() {
    for (var i = 0; i < reload_listeners.length; ++i) {
        reload_listeners[i]();
    }
}
function get_locale() {
    return document.body.getAttribute("data-locale");
}
do_reload();
window.addEventListener("load", function(e) { do_reload(); });
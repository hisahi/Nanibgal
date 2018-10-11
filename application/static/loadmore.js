function load_more_handler() {
    if (document.getElementById("next-page-button") && document.getElementById("load-more-button")) {
        document.getElementById("next-page-button").parentElement.style.display = "none";
        document.getElementById("load-more-button").parentElement.style.display = "block";
        document.getElementById("load-more-button").addEventListener("click", function(e) {
            var url = document.getElementById("load-more-button").getAttribute("data-source");  
            document.getElementById("load-more-button").parentElement.textContent = "...";
            $.get(url, function(data) {
                var parent = $("body").find(".list-group");
                var el = $(data).find(".list-group");
                if (el.length) {
                    $(".next-page-button").remove();
                    $(".load-more-button").remove();
                    var found_primaries = false;
                    el.children().each(function(i, e) {
                        if ($(e).hasClass("list-group-item-secondary")) {
                            if (found_primaries)
                                parent.append(e);
                        } else {
                            found_primaries = true;
                            parent.append(e);
                        }
                    });
                } else {
                    document.location.reload();
                }
            });
        });
    }
};
add_reload_listener(load_more_handler);
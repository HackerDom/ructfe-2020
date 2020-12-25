function normalizeForm() {
    normalizeFormWithParams(0.5, 0.6, 0.4, 1.23);
}


function normalizeFormWithParams(x, y, w, k) {
    let chest = $("#cont");
    let pos = chest.offset();
    let normalObj = $("#reg");

    if (normalObj.length === 0) {
        return ;
    }

    normalObj.offset({
        left: pos.left + chest.width() * x,
        top: pos.top + chest.height() * y,
    });

    normalObj.width(chest.width() * w);

    moveButton(k);
}


function moveButton(k) {
    let actionButton = $("#act-btn");
    let pos = actionButton.offset();
    let changeButton = $("#chg-btn");
    changeButton.offset({
        top: pos.top,
        left: pos.left + actionButton.width() * k,
    });
    changeButton.on("click", function () {
        if (location.href.includes("login")) {
            location.href = "/register_page";
        } else {
            location.href = "/login_page";
        }
    });
}


function main() {
    normalizeForm();
}


$(document).ready(function() {
    normalizeForm();
    $(window).resize(function() {
        normalizeForm();
    });
    normalizeForm();
    main();
    for (let i = 0; i < 10; i++) {
        setTimeout('normalizeForm()', 100 * i);
    }
});

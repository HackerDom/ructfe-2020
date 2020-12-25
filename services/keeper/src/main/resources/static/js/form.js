const loginRegex = /^[a-zA-Z0-9]{3,30}$/;


function setCheckLoginHandler() {
    let isLogin = location.href.includes("login");

    $("#reg-form").on("submit", function (e) {
        let login = $("#lgn-fld").val();
        let password = $("#psw-fld").val();

        if (!loginRegex.test(login)) {
            alert(`Incorrect login. It must match regex: ${loginRegex}`);
            return false;
        }
        if (isLogin && !isValidPair(login, password)) {
            alert("Incorrect pair (login, password)");
            return false;
        }
        if (!isLogin && isLoginExists(login)) {
            alert("This login already exists");
            return false;
        }
    });
}


function isValidPair(username, password) {
    let result = false;
    $.get({
        url: `/check_pair?login=${username}&password=${password}`,
        success: function (e) {
            result = e === "true";
        },
        error: function (e) {
            console.log(e);
        },
        async:false
    });
    return result;
}


function isLoginExists(username) {
    let result = false;
    $.get({
        url: `/is_exists?login=${username}`,
        success: function (e) {
            result = e === "true";
        },
        error: function (e) {
            console.log(e);
        },
        async:false
    });
    return result;
}


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
    setCheckLoginHandler();
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

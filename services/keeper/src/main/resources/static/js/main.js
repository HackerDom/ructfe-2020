let uploadFilename = null;


$(document).ready(function() {
    main();
});


function listFiles() {
    let files = null;
    $.get({
        url: "/files/" + path.join("/"),
        success: function (e) {
            files = e;
        },
        async:false
    });
    return files;
}


function buildFileUrl(filename) {
    return "/files/" + (path.concat([filename])).join("/");
}

function catFile(filename) {
    let result = null;
    $.get({
        url: buildFileUrl(filename),
        success: function (e) {
            result = e;
        },
        error: function (e) {
            console.log(e);
        },
        async:false
    });
    if (typeof result !== "string") {
        return null;
    }
    return result;
}


function isFile(filename) {
    return catFile(filename) !== null;
}


function buildPrompt() {
    return `${username}@keeper:${(['~'].concat(path)).join('/')} `;
}


function processLS(args, term) {
    listFiles().forEach(function (name) {
        term.echo(name);
    });
}


function processHelp(args, term) {
    let cmds = Object.keys(processors);
    term.echo(`Commands list:\n${cmds.join("\n")}`);
}


function processCD(args, term) {
    let newPathParts = args[0].split("/");
    let oldPath = [...path];

    newPathParts.forEach(function (pathPart) {
        if (pathPart === "..") {
            if (path.length !== 0) {
                path.pop();
            }
        } else {
            path.push(pathPart);
            let res = listFiles();
            if (res === null || typeof res !== "object") {
                term.echo(`Incorrect path '${args[0]}'`);
                path = oldPath;
            }
        }
    });
    term.set_prompt(buildPrompt());
}


function processCAT(args, term) {
    let catPath = args[0];
    let fileContent = catFile(catPath);
    if (fileContent === null) {
        term.echo(`No such file '${catPath}'`);
    } else {
        term.echo(fileContent);
    }
}


function processPWD(args, term) {
    term.echo((["~"].concat(path)).join("/"));
}


function processDownload(args, term) {
    if (args.length === 0 || args[0].length === 0) {
        term.echo("Pass one argument as filename to download");
        return;
    }
    let filename = args[0];
    if (!isFile(filename)) {
        term.echo(`No such file '${filename}'`);
    } else {
        let url = `/files/${(path.concat([filename])).join("/")}`;
        window.open(url, '_blank');
    }
}


function processUpload(args, term) {
    if (args.length === 0 || args[0].length === 0) {
        term.echo("Pass one argument as filename to upload");
        return;
    }
    if (args[0].includes("/")) {
        term.echo("Incorrect filename");
        return;
    }
    uploadFilename = args[0];
    $("#ufile").click();
}


function processMkdir(args, term) {
    if (args.length === 0 || args[0].length === 0) {
        term.echo("Pass one argument as directory name to create");
        return;
    }
    let newDirName = args[0];
    if (newDirName.includes("/")) {
        term.echo("Incorrect directory name");
        return;
    }
    let formData = new FormData();
    fetch(buildFileUrl(newDirName), {method: "POST", body: formData});
}


function clearCookies() {
    let cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i];
        const eqPos = cookie.indexOf("=");
        const name = eqPos > -1 ? cookie.substr(0, eqPos) : cookie;
        document.cookie = name + "=;expires=Thu, 01 Jan 1970 00:00:00 GMT";
    }
}


function processLogout(args, term) {
    clearCookies();
    location.reload();
}


const processors = {
    'ls': processLS,
    'cd': processCD,
    'cat': processCAT,
    'pwd': processPWD,
    'download': processDownload,
    'upload': processUpload,
    'mkdir': processMkdir,
    'logout': processLogout,
    'help': processHelp,
};


function main() {
    jQuery(function ($, undefined) {
        $('#terminal').terminal(function (line, term) {
            if (line === '') {
                return;
            }
            let parts = line.split(' ');
            if (parts.length === 0) {
                return;
            }
            let cmd = parts[0];
            let args = parts.slice(1);
            if (!Object.keys(processors).includes(cmd)) {
                term.echo(`No such command '${cmd}'`);
            } else {
                processors[cmd](args, term);
            }
        }, {
            greetings: "Hello there! Keeper is a service for keeping any files. Type 'help' for command list. Have fun! :3",
            name: 'js_demo',
            prompt: cmd_prompt
        });
    });

    $("#ufile").on("change", function (e) {
        let file = $("#ufile")[0].files[0];
        file.name = uploadFilename;
        let formData = new FormData();

        formData.append("file", file);
        fetch(buildFileUrl(uploadFilename), {method: "POST", body: formData});
    });
}

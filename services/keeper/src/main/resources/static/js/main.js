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
        error: function (e) {
            console.log(e);
        },
        async:false
    });
    return files;
}


function catFile(filename) {
    let result = null;
    $.get({
        url: "/files/" + (path.concat([filename])).join("/"),
        success: function (e) {
            result = e;
        },
        error: function (e) {
            console.log(e);
        },
        async:false
    });
    return result;
}


function buildPrompt() {
    return `${username}@keeper:${(['~'].concat(path)).join('/')} `;
}


// function getCommandArgs(parts, cmd) {
//     if (parts.length === 0) {
//         return null
//     }
//     if (parts[0] === cmd) {
//         return parts
//     }
// }


function processLS(args, term) {
    listFiles().forEach(function (name) {
        term.echo(name);
    });
}


function processCD(args, term) {
    let newPath = args[0];
    if (!listFiles().includes(newPath) && newPath !== "..") {
        term.echo(`No such file or directory: '${newPath}'`);
    } else {
        if (newPath === "..") {
            if (path.length !== 0) {
                path.pop();
            }
        } else {
            path.push(newPath);
            let res = listFiles();
            if (typeof(res) !== "object") {
                term.echo(`Incorrect path '${newPath}'`);
                path.pop();
            }
        }
    }
    term.set_prompt(buildPrompt());
}


function processCAT(args, term) {
    let catPath = args[0];
    let fileContent = catFile(catPath);
    if (fileContent === null) {
        console.log("!");
    } else {
        term.echo(fileContent);
    }
}


function processPWD(args, term) {
    term.echo((["~"].concat(path)).join("/"));
}


const processors = {
    'ls': processLS,
    'cd': processCD,
    'cat': processCAT,
    'pwd': processPWD,
};


function main() {
    jQuery(function ($, undefined) {
        $('#term_demo').terminal(function (line, term) {
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
            greetings: 'Javascript Interpreter',
            name: 'js_demo',
            // height: '100%',
            // width: 450,
            prompt: cmd_prompt
            // prompt: 'user@keeper: ~/path '
        });
    });
}

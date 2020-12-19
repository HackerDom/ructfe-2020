
function Shape(x, y, w, h, text, fill, font, clickHandler) {
    this.x = x || 0;
    this.y = y || 0;
    this.w = w || 0;
    this.h = h || 0;
    this.text = text;
    this.fill = fill || '#AAAAAA';
    this.font = font || '30px Arial';
    this.selected = false;
    this.clickHandler = clickHandler;
}

Shape.prototype.draw = function(ctx) {
    ctx.font = this.font;
    ctx.fillStyle = this.selected ? 'red' : this.fill;
    if (this.text) {
        enableShadow(ctx);
        ctx.fillText(this.text, this.x, this.y + this.h);
        disableShadow(ctx);
    } else {
        ctx.fillRect(this.x, this.y, this.w, this.h);
    }
}

Shape.prototype.contains = function(mx, my) {
    return (this.x <= mx) && (this.x + this.w >= mx) &&
        (this.y <= my) && (this.y + this.h >= my);
}

function CanvasState(canvas) {
  
    this.canvas = canvas;
    this.width = canvas.width;
    this.height = canvas.height;
    this.ctx = canvas.getContext('2d');
  
    var stylePaddingLeft, stylePaddingTop, styleBorderLeft, styleBorderTop;
    if (document.defaultView && document.defaultView.getComputedStyle) {
        this.stylePaddingLeft = parseInt(document.defaultView.getComputedStyle(canvas, null)['paddingLeft'], 10) || 0;
        this.stylePaddingTop = parseInt(document.defaultView.getComputedStyle(canvas, null)['paddingTop'], 10) || 0;
        this.styleBorderLeft = parseInt(document.defaultView.getComputedStyle(canvas, null)['borderLeftWidth'], 10) || 0;
        this.styleBorderTop = parseInt(document.defaultView.getComputedStyle(canvas, null)['borderTopWidth'], 10) || 0;
    }
    var html = document.body.parentNode;
    this.htmlTop = html.offsetTop;
    this.htmlLeft = html.offsetLeft;

    this.valid = false;
    this.dlgstate = 'idle';
    this.shapes = [];
    this.input = '';
    var myState = this;

    canvas.addEventListener('selectstart', function(e) {
        e.preventDefault();
        return false;
    }, false);

    canvas.addEventListener('click', function(e) {
        var mouse = myState.getMouse(e);
        var mx = mouse.x;
        var my = mouse.y;
        var shapes = myState.shapes;
        var l = shapes.length;
        for (var i = l - 1; i >= 0; i--) {
            if (shapes[i].contains(mx, my)) {
                if (shapes[i].clickHandler)
                    shapes[i].clickHandler(myState, shapes[i]);
                return;
            }
        }
    }, true);
    window.addEventListener('keypress', function (e) {
        if (myState.dlgstate != 'save')
            return;
        if (e.keyCode == 13) {
                doSave(myState);
        }
        else {
            if (myState.input.length < 10)
                myState.input += String.fromCharCode(e.keyCode).toUpperCase();
        }
    }, true);
    window.addEventListener('keydown', function (e) {
        if (myState.dlgstate != 'save')
            return;
        if (e.keyCode == 8 || e.keyCode == 46) {
            if (myState.input)
                myState.input = myState.input.substr(0, myState.input.length - 1);
        } else if (e.keyCode == 127) {
            myState.dlgstate = '';
        }
        myState.valid = false;
    }, true);

    this.interval = 30;
    setInterval(function() {
        myState.draw();
    }, myState.interval);
}

CanvasState.prototype.addShape = function(shape) {
    this.shapes.push(shape);
    this.valid = false;
}

CanvasState.prototype.clear = function() {
    this.ctx.clearRect(0, 0, this.width, this.height);
}

CanvasState.prototype.draw = function() {
    if (!this.valid) {
        var ctx = this.ctx;
        var shapes = this.shapes;
        this.clear();

        drawGlass(this, ctx);

        var l = shapes.length;
        for (var i = 0; i < l; i++) {
            shapes[i].draw(ctx);
        }

        this.valid = true;
    }
}

function drawLowerEllipseRtl(ctx, centerX, centerY, width, height) {
    ctx.moveTo(centerX + width / 2, centerY); // A1

    ctx.bezierCurveTo(
        centerX + width / 2, centerY + height / 2, // C1
        centerX - width / 2, centerY + height / 2, // C2
        centerX - width / 2, centerY); // A2
}

function drawLowerEllipse(ctx, centerX, centerY, width, height) {
    ctx.moveTo(centerX - width / 2, centerY); // A1

    ctx.bezierCurveTo(
        centerX - width / 2, centerY + height / 2, // C1
        centerX + width / 2, centerY + height / 2, // C2
        centerX + width / 2, centerY); // A2
}

function drawUpperEllipse(ctx, centerX, centerY, width, height) {
    ctx.moveTo(centerX - width / 2, centerY); // A1

    ctx.bezierCurveTo(
        centerX - width / 2, centerY - height / 2, // C1
        centerX + width / 2, centerY - height / 2, // C2
        centerX + width / 2, centerY); // A2
}

function drawGlass(s, ctx) {
    ctx.beginPath();
    drawUpperEllipse(ctx, s.width / 2, s.height - 350, 225, 50);
    ctx.lineTo(s.width / 2 + 150 / 2, s.height - 50);
    drawLowerEllipseRtl(ctx, s.width / 2, s.height - 50, 150, 50);
    ctx.lineTo(s.width / 2 - 225 / 2, s.height - 350);

    ctx.fillStyle = 'rgba(250, 250, 250, 0.05)';
    ctx.fill();

    ctx.strokeStyle = 'rgba(250, 250, 250, 0.2)';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.beginPath();
    drawLowerEllipseRtl(ctx, s.width / 2, s.height - 350, 225, 50);
    ctx.lineTo(s.width / 2 - 150 / 2, s.height - 50);
    drawUpperEllipse(ctx, s.width / 2, s.height - 50, 150, 50);
    ctx.lineTo(s.width / 2 + 225 / 2, s.height - 350);

    ctx.strokeStyle = 'rgba(250, 250, 250, 0.2)';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.beginPath();
    drawLowerEllipse(ctx, s.width / 2, s.height - 350, 225, 50);
    ctx.lineTo(s.width / 2 - 150 / 2, s.height - 50);
    drawLowerEllipseRtl(ctx, s.width / 2, s.height - 50, 150, 50);
    ctx.lineTo(s.width / 2 + 225 / 2, s.height - 350);

    ctx.fillStyle = 'rgba(250, 250, 250, 0.15)';
    ctx.fill();
}

CanvasState.prototype.getMouse = function(e) {
    var element = this.canvas,
        offsetX = 0,
        offsetY = 0,
        mx, my;

    if (element.offsetParent !== undefined) {
        do {
            offsetX += element.offsetLeft;
            offsetY += element.offsetTop;
        } while ((element = element.offsetParent));
    }

    offsetX += this.stylePaddingLeft + this.styleBorderLeft + this.htmlLeft;
    offsetY += this.stylePaddingTop + this.styleBorderTop + this.htmlTop;

    mx = e.pageX - offsetX;
    my = e.pageY - offsetY;

    return {
        x: mx,
        y: my
    };
}

function loadData(url, handler) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            handler(this.status, this.responseText);
        }
    };
    xhttp.open("GET", url, true);
    xhttp.send();
}

function makeColor(c, a, d)
{
    d = d || 0;
    return 'rgba(' + 
        Math.max(0, parseInt(c.substr(0, 2), 16) - d) + ',' + 
        Math.max(0, parseInt(c.substr(2, 2), 16) - d) + ',' + 
        Math.max(0, parseInt(c.substr(4, 2), 16) - d) + ',' + a + ')';
}

function addLiquid(state, h)
{
    var a1 = parseInt(h.substr(14, 2), 16) / 255;
    var a2 = parseInt(h.substr(12, 2), 16) / 255;
    var c1 = h.substr(0, 6);
    var c2 = h.substr(6, 6);

    var obj = {};
    obj.contains = function () {};
    obj.draw = function (ctx) {
        var grd = ctx.createLinearGradient(state.width / 2, state.height - 280, state.width / 2, state.height - 50);
        grd.addColorStop(0, makeColor(c1, a1 * 0.8));
        grd.addColorStop(1, makeColor(c2, a2 * 0.8));

        ctx.beginPath();
        drawUpperEllipse(ctx, state.width / 2, state.height - 280, 205, 50);
        ctx.lineTo(state.width / 2 + 150 / 2, state.height - 50);
        drawLowerEllipseRtl(ctx, parseInt(state.width / 2), state.height - 50, 150, 50);
        ctx.lineTo(state.width / 2 - 205 / 2, state.height - 280);

        ctx.fillStyle = grd;
        ctx.fill();

        ctx.beginPath();
        drawUpperEllipse(ctx, parseInt(state.width / 2), state.height - 280, 205, 50);
        drawLowerEllipseRtl(ctx, parseInt(state.width / 2), state.height - 280, 205, 50);

        ctx.fillStyle = makeColor(c1, a1 * 0.8);
        ctx.fill();

        ctx.strokeStyle = makeColor(c1, a1, 20);
        ctx.beginPath();
        drawUpperEllipse(ctx, parseInt(state.width / 2), state.height - 280, 205, 50);
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.beginPath();
        drawLowerEllipseRtl(ctx, parseInt(state.width / 2), state.height - 280, 205, 50);
        ctx.lineWidth = 2;
        ctx.stroke();
    };
    state.shapes = [obj].concat(state.shapes);
}

function doMixNew(state)
{
    var recipe = [];
    for (var i = 0; i < state.shapes.length; i++) {
        if (state.shapes[i].selected)
        {
            recipe.push(state.shapes[i].text);
            recipe.push(state.shapes[i].text);
            recipe.push(state.shapes[i].text);
        }
    }
    state.recipe = recipe.join(',');
    var req = 'mixnew?what=' + state.recipe;
    loadData(req, function (status, resp) {
        if (status != 200)
            alert(status);
        addLiquid(state, resp);
        state.dlgstate = 'save';
        state.valid = false;
    });
}
function doMix(state)
{
    var name = '';
    for (var i = 0; i < state.shapes.length; i++) {
        if (state.shapes[i].selected)
        {
            name = state.shapes[i].text;
        }
    }
    var req = 'mix?name=' + name;
    loadData(req, function (status, resp) {
        if (status != 200)
            alert(status);
        addLiquid(state, resp);
        state.dlgstate = '';
        state.valid = false;
    });
}
function doSave(state)
{
    var req = 'memorize?name=' + state.input + '&what=' + state.recipe;
    loadData(req, function (status, resp) {
        if (status != 201)
            alert(status);
        else {
            alert('Done! Your recipe is called ' + resp);
        }
        state.dlgstate = '';
        state.valid = false;
    });
}
function enableShadow(ctx)
{
    ctx.shadowColor = 'black';
    ctx.shadowOffsetX = 2;
    ctx.shadowOffsetY = 2;
    ctx.shadowBlur = 5;
}
function disableShadow(ctx)
{
    ctx.shadowColor = 'rgba(0,0,0,0)';
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 0;
    ctx.shadowBlur = 0;
}

spirits = [
    "Ale",
    "Porter",
    "Stout",
    "Lager",
    "Cider",
    "Mead",
    "Wine",
    "Port",
    "Sherry",
    "Vermouth",
    "Vinsanto",
    "Sangria",
    "Champagne",
    "Sake",
    "Brandy",
    "Cognac",
    "Armagnac",
    "Schnapps",
    "Gin",
    "Horilka",
    "Metaxa",
    "Rakia",
    "Rum",
    "Shochu",
    "Soju",
    "Tequila",
    "Vodka",
    "Bourbon",
    "Whiskey",
    "Absinthe",
    "Juice",
    "Cola",
    "Water"
];

function init() {
    var s = new CanvasState(document.getElementById('canvas1'));

    var textBrush = 'rgba(250,250,250,0.9)';
    var backBrush = 'rgba(0,0,0,0.4)';

    var multiselHandler = function (state, shape) {
      if (state.dlgstate == 'idle' || state.dlgstate == 'mixsel')
      {
        shape.selected ^= 1;
        var selectedShapes = 0;
        for (var i = 0; i < state.shapes.length; i++)
          selectedShapes += state.shapes[i].selected ? 1 : 0;
        state.dlgstate = selectedShapes ? 'mixsel' : 'idle';
        state.valid = false;
      }
    };
    var selHandler = function (state, shape) {
      if (state.dlgstate == 'idle')
      {
        shape.selected = true;
        state.dlgstate = 'mix';
        doMix(state);
      }
    };

    s.addShape(new Shape(80, 20, 380, 650, null, backBrush));
    s.addShape(new Shape(s.width - 450, 20, 380, 650, null, backBrush));

    loadData('list?skip=0&take=10', function(status, text) {
        if (status != 200)
            return;
        var lines = text.split('\n');
        for (var i = 0; i < lines.length; i++) {
            if (lines[i] == '')
                continue;
            s.addShape(new Shape(s.width - 400, 100 + 30 * i, 150, 20, lines[i], textBrush, '20px Arial', selHandler));
        }
    });
    for (var i = 0; i < parseInt(spirits.length / 2); i++) {
        s.addShape(new Shape(150, 100 + 30 * i, 150, 20, spirits[i], textBrush, '20px Arial', multiselHandler));
    }
    for (var i = parseInt(spirits.length / 2); i < spirits.length; i++) {
        s.addShape(new Shape(310, 100 + 30 * (i - parseInt(spirits.length / 2)), 150, 20, spirits[i], textBrush, '20px Arial', multiselHandler));
    }

    s.addShape(new Shape(180, 50, 150, 30, 'Mix yourself', textBrush, '35px Arial'));
    s.addShape(new Shape(s.width - 350, 50, 150, 30, 'Order existing', textBrush, '35px Arial'));

    var mixbtn = new Shape(200, 600, 180, 60, 'Mix this', textBrush, '40px Arial',
        function (state, shape) {
            if (state.dlgstate == 'mixsel') {
                state.dlgstate = 'mixnew';
                doMixNew(state);
            }   
        });
    mixbtn.draw = function(ctx) {
        if (s.dlgstate != 'mixsel')
            return;

        enableShadow(ctx);
        ctx.fillStyle = 'rgba(140, 30, 30, 0.9)';
        ctx.fillRect(this.x - 20, this.y + 15, this.w, this.h);
        ctx.font = this.font;
        ctx.fillStyle = this.fill;
        ctx.fillText(this.text, this.x, this.y + this.h);
        disableShadow(ctx);
    };
    s.addShape(mixbtn);
    var nameback = new Shape(parseInt(s.width / 2 - 150) - 20, 500, 400, 130, 'How should we call it?', textBrush, '20px Arial');
    nameback.draw = function(ctx) {
        if (s.dlgstate != 'save')
            return;

        enableShadow(ctx);
        ctx.fillStyle = 'rgba(140, 30, 30, 1)';
        ctx.fillRect(this.x - 20, this.y + 15, this.w, this.h);
        ctx.font = this.font;
        ctx.fillStyle = this.fill;
        ctx.fillText(this.text, this.x, this.y + 50);
        disableShadow(ctx);
    };
    s.addShape(nameback);
    var namefld = new Shape(parseInt(s.width / 2 - 150), 550, 360, 60, '', 'black', '40px Arial');
    namefld.draw = function(ctx) {
        if (s.dlgstate != 'save')
            return;

        ctx.fillStyle = 'rgba(250, 250, 250, 1)';
        ctx.fillRect(this.x - 20, this.y + 15, this.w, this.h);
        ctx.font = this.font;
        ctx.fillStyle = this.fill;
        ctx.fillText(s.input, this.x, this.y + this.h);
    };
    s.addShape(namefld);
}

(function() {
    var canvas = document.getElementById('canvas1');

    window.addEventListener('resize', resizeCanvas, false);

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        init();
    }
    resizeCanvas();
})();
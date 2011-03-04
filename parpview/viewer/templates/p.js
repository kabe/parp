document.write('<script type="text/javascript" src="/script/prototype.js"></script>');
document.write('<script type="text/javascript" src="/script/tooltip.js"></script>');

Event.observe(window,"load",function() {
        $$("*").findAll(function(node){
                return node.getAttribute('title');
            }).each(function(node){
                    new Tooltip(node,node.title);
                    node.removeAttribute("title");
                });
    });

function makeIndex() {
    var str = "<ul>\n";
    var headers = $$('h1');
    for (var i = 0; i < headers.length; i++) {
        var a = headers[i];
        str += "<li><a href=\""
            + "#" + a.id + "\">" + a.innerHTML.stripTags() + "</a>\n";
    }
    str += "</ul>\n";
    $('toc').innerHTML = str;
}

function seemorefunc() {
    var hidden_trs = $$('tr.hiddentrs');
    $('seemore_tr').hide();
    $('hide_tr').show();
    hidden_trs.each(Element.show);
}

function hidefunc() {
    var hidden_trs = $$('tr.hiddentrs');
    $('seemore_tr').show();
    $('hide_tr').hide();
    hidden_trs.each(Element.hide);
}

function submitform(colnum) {
    var form = $('choiceform');
    var condition = 'input[type="radio"]';
    var radios = $('coldef_table').select(condition);
    radios.each(function(x) {
            if (x.hasAttribute('name')) {
                if(x.readAttribute('name') == 'order') {
                    if (x.hasAttribute('value')) {
                        if(x.readAttribute('value') == colnum) {
                            x.writeAttribute('checked', 'checked');
                        }
                    }
                }
            }
        });
    form.submit();
    return false;
}

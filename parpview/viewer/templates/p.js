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


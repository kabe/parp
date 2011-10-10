var changed_indeces = new Array();
var enabled_indeces = new Array();
var disabled_indeces = new Array();

function valueChanged(index) {
    var found_in_changed = false;
    for(var i = 0; i < changed_indeces.length; i++) {
        if(changed_indeces[i] == index) {
            found_in_changed = true;
        }
    }
    if(found_in_changed == false) {
        changed_indeces.push(index);
    }
    element_id = "#wfe_" + index;
    if($(element_id)[0].checked) {
        for(var i = 0; i < disabled_indeces.length; i++) {
            if(disabled_indeces[i] == index) {
                delete disabled_indeces[i];
            }
        }
        enabled_indeces.push(index);
    } else {
        for(var i = 0; i < enabled_indeces.length; i++) {
            if(enabled_indeces[i] == index) {
                delete enabled_indeces[i];
            }
        }
        disabled_indeces.push(index);
    }
}

function submitChanges() {
    var changed_str = changed_indeces.join(" ");
    var enabled_str = enabled_indeces.join(" ");
    var disabled_str = disabled_indeces.join(" ");
    // Create form
    var form = document.createElement("form");
    document.body.appendChild(form);
    var cinput = document.createElement("input");
    cinput.setAttribute("type", "hidden");
    cinput.setAttribute("name", "wf_changed");
    cinput.setAttribute("value", changed_str);
    form.appendChild(cinput);
    var einput = document.createElement("input");
    einput.setAttribute("type", "hidden");
    einput.setAttribute("name", "wf_enabled");
    einput.setAttribute("value", enabled_str);
    form.appendChild(einput);
    var dinput = document.createElement("input");
    dinput.setAttribute("type", "hidden");
    dinput.setAttribute("name", "wf_disabled");
    dinput.setAttribute("value", disabled_str);
    form.appendChild(dinput);
    form.setAttribute("action", "");
    form.setAttribute("method", "post");
    $(form).append(csrf_token);
    // Submit form
    form.submit();
    // Clear
    changed_indeces = new Array();
    enabled_indeces = new Array();
    disabled_indeces = new Array();
}

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
    // Async POST
    $.post("",
           {
               wf_changed: changed_str,
               wf_enabled: enabled_str,
               wf_disabled: disabled_str
           });
    // Clear
    changed_indeces = new Array();
    enabled_indeces = new Array();
    disabled_indeces = new Array();
}

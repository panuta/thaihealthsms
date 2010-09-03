// Add comma as user is typing number
$.fn.digits = function(){
    return this.each(function(){
        $(this).keyup(function(){
            var $this = $(this);
            var num = $this.val().replace(/,/g, '');
            // the following line has been simplified. Revision history contains original.
            $this.val(num.replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,"));
        });
    })
}

function is_number(str) {
    var charcode = 0;
    
    for (var i=0;i<str.length;i++) {
        charcode = str.charCodeAt(i);
        if(!(charcode >= 48 && charcode <= 57)) {
            return false;
        }
    }
    return true;
}

function to_number(str) {
    if(str.indexOf(".") != -1) {
        str = str.substring(0, str.indexOf("."));
    }
    
    do {
        str = str.replace(",", "");
    } while(str != str.replace(",", ""));
    str = str.replace(",", "");
    
    if(!is_number(str)) return null;
    return parseInt(str);
}

function to_discrete_num_string(str){
    if(str.indexOf(".") != -1) {
        return null;
    } else {
        str = str.replace(",", "");
        if(!is_number(str)) return null;
    }
    
    return str;
}
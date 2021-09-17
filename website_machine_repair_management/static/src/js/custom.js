odoo.define('website_machine_repair_management.garantee', function (require) {
    'use strict';
// Owl slider
$(document).ready(function(){
    $(".oe_website_sale").on("change",".under_guarantee", function(event){
        var under_guarantee = $(".under_guarantee").val();
        if (under_guarantee == "yes"){
            $(".type_guarantee").css("display","block");
        }else{
            $(".type_guarantee").css("display","none");
        }
    });
 });
});

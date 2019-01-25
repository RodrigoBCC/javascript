$(document).ready(function() {
    function getCeleryinfoBD(data_id) {
        $.ajax({
            url : "/task_fail/", //from what I know, this URL is where the AJAX will go after processing
            type: "POST",
            data: {'data_id': data_id},
            async: true,
            success: function(json) {
                for (i in json){
                    if (json[i][1] == "FAILURE"){

                    }
                    
                }
            }
        })
    }

    function getCeleryInformation() {
        $.ajax({
            url : "/task_progress", //from what I know, this URL is where the AJAX will go after processing
            type: "GET",
            async: true,
            success: function(json) {
                // console.log(json);
                var count = 0;
                for (i in json){
                    if (json[i].state == "PENDING") {
                        
                    }
                    else if (json[i].state == "FAILURE") {

                    } 
                    else {

                    }
                }
                if (count>0) {
                    setTimeout(getCeleryInformation(), 5000);
                }else{
                    return 0
                }
            }     
        })
    }
});
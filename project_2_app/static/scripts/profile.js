console.log('in-sanity check');

$(document).ready( function() {
    
    const csrfToken = getCookie('csrftoken');

    $('button.btn-remove').on('click', function() {
        var $parent= $(this).parent();
        var $article_data_id= $parent.attr('data-id');
        console.log('remove=',$article_data_id);
        
        var dataToSend= {"youtube_id":$article_data_id};
        $.ajax({
            "method": "DELETE",
            "url": "/user/remove_like_dislike/",
            "contentType": "application/json",
            "dataType": "json",
            "data": dataToSend,
            "beforeSend": function(xhr) {
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
            },
            "success": function(json) {
                console.log(json);
                if (json.message=="successfully deleted") {
                    //$(`article[data-id=${$article_data_id}]`).fadeOut();
                    $(`article[data-id=${$article_data_id}]`).remove();
                }
                
            }, 
            "error": function(e1,e2,e3) { console.log('e1= ',e1,', e2= ',e2,', e3= ',e3); }
    
        });


    });

    
});
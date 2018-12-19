console.log('in-sanity check');

var $initProfileVal;

function instantUpdateByID(field,target,oldTag,csrfToken) {
    // click on area to change
    $(target).on('click',`${oldTag}[id=${field}]`,function(){
        $initProfileVal= $(this).html();
        $(this).replaceWith($(`<input id='${field}' value='${$(this).html()}' required>`));
        $(`${target} input[id=${field}]`).focus();
    });

    $(target).on('blur',`input[id=${field}]`,function(){
        var $text= $(this).val();
        if ($text=='') return;
        $(this).replaceWith($(`<${oldTag} id='${field}'>${$text}</${oldTag}>`));
        if ($text.trim()==$initProfileVal.trim()) return;
        var dataObj={}; dataObj[field]= $text;
        console.log(dataObj);
        //return;
        $.ajax({
            'type': 'PATCH',
            'url': '/user/profile_edit/',
            'data': JSON.stringify(dataObj),
            'contentType': 'application/json',
            'beforeSend': function(xhr) {
                xhr.setRequestHeader('X-CSRFToken', csrfToken);
            },
            'success': function(output){ 
                console.log('output:',output);
                /*
                var key= Object.getOwnPropertyNames(output)[0];
                if (key=='username') { $('i[name=user]').html(output[key]); } 
                $(`#${key}`).html(output[key]);
                */
            },
            'error': function(err1,err2,err3) { console.log(err1,err2,err3); }
        });
    });
}


$(document).ready( function() {
    
    const csrfToken = getCookie('csrftoken');

    instantUpdateByID('email','p','span',csrfToken)


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
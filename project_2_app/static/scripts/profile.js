console.log('in-sanity check');

var $initProfileVal;

// helper function: instant update based on target and id
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
        
        $.ajax({
            'type': 'PATCH',
            'url': '/user/profile_edit/',
            'data': JSON.stringify(dataObj),
            'contentType': 'application/json',
            'beforeSend': function(xhr) { xhr.setRequestHeader('X-CSRFToken', csrfToken); },
            'success': function(output,textStatus, xhr){ 
                console.log(xhr.status);
                console.log('output:',output);
            },
            'error': function(err1,err2,err3) { console.log(err1,err2,err3); }
        });
    });
}


$(document).ready( function() {
    
    const csrfToken = getFromCookie('csrftoken');

    // hide update profile_pic form
    $('.update_profile_pic_form').hide();

    // instant update email 
    instantUpdateByID('email','p','span',csrfToken);

    // update profile_pic button toggle
    $('button[name=edit_profile_pic]').on('click',function(){
        $(this).hide();
        $('.update_profile_pic_form').show();
    });

    // cancel update profile_pic form
    $('button[name=cancel_update_profile_pic]').on('click',function(event){
        event.preventDefault();
        $('.update_profile_pic_form').hide();
        $('button[name=edit_profile_pic]').show();
    });

    $('button[name=analyze]').on('click',function(){
        window.location.href='/analysis/';
    });

    // save update profile_pic form
    $('button[name=save_update_profile_pic]').on('click',function(event){
        event.preventDefault();
        var $profile_pic= $('#profile_pic').val();
        if ($profile_pic=='') return;
        var form_data = new FormData();
        form_data.append('image', $('#profile_pic')[0].files[0]);
        
        $.ajax({
            'method': 'POST',
            'url': '/user/profile_edit/',
            'data': form_data,
            'processData': false,
            'contentType': false,
            'beforeSend': function(xhr) { xhr.setRequestHeader('X-CSRFToken', csrfToken); },
            'success': function(json, textStatus, xhr) {
                console.log(json);
                if (xhr.status==200) {
                    $('img.profile_pic_display').attr('src',json.img_url);
                    $('.update_profile_pic_form').hide();
                    $('button[name=edit_profile_pic]').show();
                }
            },
            'error': function(e1,e2,e3) { console.log('e1= ',e1,', e2= ',e2,', e3= ',e3); }
        });
    });

    // remove video from likes / dislikes list
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
            "beforeSend": function(xhr) { xhr.setRequestHeader('X-CSRFToken', csrfToken); },
            "success": function(json,textStatus, xhr) {
                console.log(json);
                if (xhr.status==200) {
                    //$(`article[data-id=${$article_data_id}]`).fadeOut();
                    $(`article[data-id=${$article_data_id}]`).remove();
                }
            }, 
            "error": function(e1,e2,e3) { console.log('e1= ',e1,', e2= ',e2,', e3= ',e3); }
        });
    });
    
});
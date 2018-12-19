console.log('in-sanity check');

function getCookie(name) {
    if (!document.cookie) {
      return null;
    }
  
    const xsrfCookies = document.cookie.split(';')
      .map(c => c.trim())
      .filter(c => c.startsWith(name + '='));
  
    if (xsrfCookies.length === 0) {
      return null;
    }
  
    return decodeURIComponent(xsrfCookies[0].split('=')[1]);
}

function likes_dislike_post_ajax(parent,article_data_id,likes,csrfToken) {
    
    var dataToSend= {
        "like": likes,
        "youtube_id": article_data_id,
        "title": parent.find('h3').html(),
        "thumbnail_url": parent.find('img').attr('src'),
        //"thumbnail_width": "120",
        //"thumbnail_height": "90",
        "channel_title": parent.find('.p-channel-title').html(),
        "category_id": parent.find('.p-cat-id').html(),
        "description": parent.find('.p-description').html(),
        "tags": parent.find('.p-tags').html()
    };
    //console.log(dataToSend);

    $.ajax({
        "method": "POST",
        "url": "/add_like_dislike/",
        "data": dataToSend,
        "beforeSend": function(xhr) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        },
        "success": function(json) {
            console.log(json);
            parent.find('button').prop('disabled',true);
        }, 
        "error": function(e1,e2,e3) { console.log('e1= ',e1,', e2= ',e2,', e3= ',e3); }

    });
}


$(document).ready( function() {
    
    const csrfToken = getCookie('csrftoken');
    console.log(csrfToken);

    $('button.btn-like').on('click', function() {
        var $parent= $(this).parent();
        var $article_data_id= $parent.attr('data-id');
        console.log('like=',$article_data_id);
        likes_dislike_post_ajax($parent,$article_data_id,"True",csrfToken);
    });

    $('button.btn-dislike').on('click', function() {
        var $parent= $(this).parent();
        var $article_data_id= $parent.attr('data-id');
        console.log('dislike=',$article_data_id);
        likes_dislike_post_ajax($parent,$article_data_id,"False",csrfToken);
    });
});
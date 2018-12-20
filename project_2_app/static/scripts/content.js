console.log('in-sanity check');

// helper function: create likes / dislikes of videos 
function likes_dislike_post_ajax(parent,article_data_id,likes,csrfToken) {
    
    var dataToSend= {
        "like": likes,
        "youtube_id": article_data_id,
        "title": parent.find('h3').html(),
        "thumbnail_url": parent.find('img').attr('src'),
        "channel_title": parent.find('.p-channel-title').html(),
        "category_id": parent.find('.p-cat-id').html(),
        "description": parent.find('.p-description').html(),
        "tags": parent.find('.p-tags').html()
    };
    
    $.ajax({
        "method": "POST",
        "url": "/user/add_like_dislike/",
        "data": dataToSend,
        "beforeSend": function(xhr) { xhr.setRequestHeader('X-CSRFToken', csrfToken); },
        "success": function(json) { console.log(json); parent.find('button').prop('disabled',true); }, 
        "error": function(e1,e2,e3) { console.log('e1= ',e1,', e2= ',e2,', e3= ',e3); }
    });
}

function video_template(target,video) {
    
    target.append(`
    <article data-id='${video.youtube_id}'>
      <h3>${video.title}</h3>
      <a href='https://www.youtube.com/watch?v=${video.youtube_id}'>
        <img src='${video.thumbnail.url}' alt=''>
      </a>
      <p class='p-description'> ${video.description}</p>
      <p class='p-tags'>${video.tags}</p>
      <p class='p-channel-title'>${video.channel_title}</p>
      <p class='p-cat-id' style='display:none;'>${video.category_id }</p>
      <button class="btn-like">Like!</button>
      <button class="btn-dislike">DisLike :( </button>
    </article>`);
}


function renderVideoList(output,target) {
    console.log(output.video_results);
    target.html('');
    if (output.video_results.length==0) {
        target.html('No Result...');
    }
    output.video_results.forEach((video)=>{
        video_template(target,video);
    });
}


$(document).ready( function() {
    
    const csrfToken = getFromCookie('csrftoken');
    
    // like a video and save to DB
    $('#video_list').on('click', 'button.btn-like', function() {
        var $parent= $(this).parent();
        var $article_data_id= $parent.attr('data-id');
        //console.log('like=',$article_data_id);
        likes_dislike_post_ajax($parent,$article_data_id,"True",csrfToken);
    });

    // dislike a video and save to DB
    $('#video_list').on('click', 'button.btn-dislike', function() {
        var $parent= $(this).parent();
        var $article_data_id= $parent.attr('data-id');
        //console.log('dislike=',$article_data_id);
        likes_dislike_post_ajax($parent,$article_data_id,"False",csrfToken);
    });

    $('div.search_videos').hide();
    $('button.show-search').on('click', function() {
        if ($(this).hasClass('toggle')) {
            $('div.search_videos').hide();
            $('button.show-search.toggle').html('Search Option');
            $('button.show-search.toggle').removeClass('toggle');
        } else {
            $('button.show-search').html('Hide Search');
            $('button.show-search').addClass('toggle');
            $('div.search_videos').show();
        }
    });

    $('button.btn-get-all').on('click', function() {
        $.ajax({
            'method': 'GET',
            'url': '/video/category_all/',
            'success': function(output, textStatus, xhr) {
                if (xhr.status==200) { renderVideoList(output,$('#video_list')); }
            },
            'error': function(e1,e2,e3) { console.log('e1= ',e1,', e2= ',e2,', e3= ',e3); }
        });
    });

    $('button.btn-get-selected').on('click', function() {
        var $cat_id= $('select.category option:selected').val();
        $.ajax({
            'method': 'GET',
            'url': '/video/category_selected/',
            'data': {'cat_id': $cat_id},
            'success': function(output, textStatus, xhr) {
                if (xhr.status==200) { renderVideoList(output,$('#video_list')); }
            },
            'error': function(e1,e2,e3) { console.log('e1= ',e1,', e2= ',e2,', e3= ',e3); }
        });
        console.log($cat_id);
    });
});
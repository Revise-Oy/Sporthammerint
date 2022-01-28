odoo.define('facebook_feed_axis.fb_post', function(require) {
    'use strict';

    var ajax = require('web.ajax');

    $(".post-share-btn").click(function() {
        $(".social-icon").addClass("active");
    });

    $.ajax({
        type: "POST",
        dataType: 'json',
        url: '/facebook_id_token',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
            'jsonrpc': "2.0",
            'method': "call",
        }),

        success: function(data) {
            if (data.result.fb_background_selection == 'fb_background_image') {
                var object = data.result.custom_css;
                $('.home-facebook').attr("style", 'background-image:url("data:image/png;base64,' + data.result.fb_background_image + '");' + object);
            }
            if (data.result.fb_background_selection == 'fb_background_color') {
                $('.home-facebook').css('background-color', data.result.fb_background_color);
            }

            if (data.result.fb_background_selection == '') {
                $('.home-facebook').css('background-image', 'url("/facebook_feed_axis/static/src//img/full_bg.jpeg")');
            }

            console.log(data.result.fb_result);
            if (data.error) {
                $("#facebookfeed").after("<div class='text-center font-weight-bold'>There is an error in access token please generate and try again</div>");
                $("#loadmore").hide();
            } else if (data.result.fb_result.error) {
                $("#facebookfeed").after("<div class='text-center font-weight-bold'>There is an error in access token please generate and try again</div>");
                $("#loadmore").hide();
            } else {
                var limit = data.result.fb_result.posts.data.length;
                var $for_data = "";
                for (var i = 0; i < limit; i++) {
                    var date = new Date(data.result.fb_result.posts.data[i].created_time);
                    var current_date = (date.getDate() + ' ' + date.getMonth() + ' ' + date.getFullYear());
                    if (data.result.fb_result.posts.data[i].likes) {
                        var likes_count = data.result.fb_result.posts.data[i].likes.data;
                    } else {
                        var likes_count = '';
                    }
                    if (data.result.fb_result.posts.data[i].comments) {
                        var comments_count = data.result.fb_result.posts.data[i].comments.data;
                    } else {
                        var comments_count = '';
                    }
                    if (data.result.fb_result.posts.data[i].message) {
                        var message = data.result.fb_result.posts.data[i].message;
                    } else {
                        var message = '';
                    }
                    $for_data += '<div class="grid-item card border-0 mt-2"><div class="card-box-shadow"><div class="card-body"><div class="row pb-sm-3 pb-2"><div class="col-3 text-center"><img class="rounded-circle img-fluid" src="' + data.result.fb_image_url + '" /></div><div class="col-9 pl-0"><a class="d-block" href="http://www.facebook.com/' + data.result.fb_page_id + '">' + data.result.fb_result.posts.data[i].from.name + '</a><small class="text-muted">' + current_date + '</small></div></div><p class="card-text text-secondary more">' + message + '</p></div><img class="img-fluid" src="' + data.result.fb_result.posts.data[i].full_picture + '" /><div class="card-body pb-4"><div class="card-post-icon text-secondary"><img src="facebook_feed_axis/static/src/img/fb-like.png" /><img src="facebook_feed_axis/static/src/img/fb-heart-icon.png" /><img src="facebook_feed_axis/static/src/img/fb-emoji-icon.png" /><img src="facebook_feed_axis/static/src/img/emoji_icon2.png" /><img src="facebook_feed_axis/static/src/img/emoji_icon3.png" /><img src="facebook_feed_axis/static/src/img/emoji_icon4.png" /><small class="pl-2">' + likes_count.length + ' likes</small><small class="px-1">' + comments_count.length + ' comments</small></div><div class="share-post pt-sm-3 pt-2 mt-sm-3 mt-2 border-top"><div class="row"><div class="col-12 px-0 text-center"><a class="d-inline-block py-1 text-primary w-100" href="https://www.facebook.com/' + data.result.fb_result.posts.data[i].id + '" title="View on Facebook"><small>View on Facebook</small></a></div></div></div></div></div></div>';
                }
                $('#facebookfeed').append($for_data);
                var $grid = $('.grid').masonry({
                    itemSelector: '.grid-item',
                    columnWidth: '.grid-sizer',
                    gutter: '.gutter-sizer',
                    horizontalOrder: true, // new!
                    percentPosition: true,
                });


                if (data.result.fb_result.posts['paging']['next']) {
                    $("#loadmore").show();
                }
                $("#page").val(1);
                $("#loadmore").on('click', function(e) {
                    /*i++;*/
                    var current_page_number = parseInt($("#page").val());
                    ajax.jsonRpc("/facebook_post_next", 'call', {
                        'page_number': current_page_number,
                    }).then(function(data) {
                        console.log(data)
                        if(data){
                            var $for_data = "";
                            var limit = data.fb_result.data.length;
                            for (var i = 0; i < limit; i++) {
                                var date = new Date(data.fb_result.data[i].created_time);
                                var current_date = (date.getDate() + ' ' + date.getMonth() + ' ' + date.getFullYear());
                                if (data.fb_result.data[i].likes) {
                                    var likes_count = data.fb_result.data[i].likes.data;
                                } else {
                                    var likes_count = '';
                                }
                                if (data.fb_result.data[i].comments) {
                                    var comments_count = data.fb_result.data[i].comments.data;
                                } else {
                                    var comments_count = '';
                                }
                                if (data.fb_result.data[i].message) {
                                    var message = data.fb_result.data[i].message;
                                } else {
                                    var message = '';
                                }
                                $for_data += '<div class="grid-item card border-0 mt-2"><div class="card-box-shadow"><div class="card-body"><div class="row pb-sm-3 pb-2"><div class="col-3 text-center"><img class="rounded-circle img-fluid" src="' + data.fb_image_url + '" /></div><div class="col-9 pl-0"><a class="d-block" href="http://www.facebook.com/' + data.fb_page_id + '">' + data.fb_result.data[i].from.name + '</a><small class="text-muted">' + current_date + '</small></div></div><p class="card-text text-secondary more">' + message + '</p></div><img class="img-fluid" src="' + data.fb_result.data[i].full_picture + '" /><div class="card-body pb-4"><div class="card-post-icon text-secondary"><img src="facebook_feed_axis/static/src/img/fb-like.png" /><img src="facebook_feed_axis/static/src/img/fb-heart-icon.png" /><img src="facebook_feed_axis/static/src/img/fb-emoji-icon.png" /><img src="facebook_feed_axis/static/src/img/emoji_icon2.png" /><img src="facebook_feed_axis/static/src/img/emoji_icon3.png" /><img src="facebook_feed_axis/static/src/img/emoji_icon4.png" /><small class="pl-2">' + likes_count.length + ' likes</small><small class="px-1">' + comments_count.length + ' comments</small></div><div class="share-post pt-sm-3 pt-2 mt-sm-3 mt-2 border-top"><div class="row"><div class="col-12 px-0 text-center"><a class="d-inline-block py-1 text-primary w-100" href="https://www.facebook.com/' + data.fb_result.data[i].id + '" title="View on Facebook"><small>View on Facebook</small></a></div></div></div></div></div></div>';
                            }

                            var $elems = $($for_data);

                            $grid.append($elems).masonry('appended', $elems);
                            if (data.fb_result['paging']['next']) {
                                $("#loadmore").show();
                            } else {
                                $("#loadmore").hide();
                            }
                            $("#page").val(current_page_number + 1)
                        }
                    });
                });

            }

        },
        error: function() {
            console.log("ERROR: <h2>Something went wrong in loading facebook post..</h2>");
        }
    });

    var checkPosition = function() {
        if ($(window).width() >= 1200) {
            //init
            var $grid = $('.grid').masonry({
                itemSelector: '.grid-item',
                masonry: {
                    column: 4
                }
            });
        }
        if ($(window).width() < 1200) {

            var $grid = $('.grid').masonry({
                itemSelector: '.grid-item',
                masonry: {
                    column: 3
                }
            });
        }
        if ($(window).width() < 768) {
            //init
            var $grid = $('.grid').masonry({
                itemSelector: '.grid-item',
                masonry: {
                    column: 2
                }
            });
        }
        if ($(window).width() < 575) {
            //init
            var $grid = $('.grid').masonry({
                itemSelector: '.grid-item',
                masonry: {
                    column: 1
                }
            });
        }

    };
    $(window).scroll(checkPosition);
});
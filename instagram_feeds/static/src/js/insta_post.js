odoo.define('instagram_feeds.insta_post', function (require) {
    'use strict';

    var ajax = require('web.ajax');


    $.ajax({
        type: "POST",
        dataType: 'json',
        url: '/instagram_id_token',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
            'jsonrpc': "2.0",
            'method': "call",
        }),
        success: function (data) {
        if (data.result.result.data){
            if (data.result.error){
                $("#instafeed").after("<div class='text-center font-weight-bold'>There is an error in access token please generate and try again</div>");
            }
            else if (data.result.result.error) {
                $("#instafeed").after("<div class='text-center font-weight-bold'>There is an error in access token please generate and try again</div>");
//                $("#loadmore").attr("style",'display:none !important');
            }
            else{            
                var limit = data.result.result.data.length;
                var $for_data = "<div class='card-columns'>";            
                var maxLength = 50;
                var removedStr = '';
                var removedStrdict = {};
                for (var i = 0; i < limit; i++) {
                    var date = new Date(data.result.result.data[i].timestamp);
                    var month = date.toLocaleString('en-us', { month: 'long' });
                    var day = date.toLocaleString('en-us', {weekday: 'long'});
                    var current_date =(day + ' ' +date.getDate() + ' ' + month + ', ' + date.getFullYear());

                    if (data.result.result.data[i].caption) {
                         var mesage = data.result.result.data[i].caption;
                    } else {
                        var mesage = '';
                    }
//                    if (data.result.result.data[i].media_type == 'VIDEO'){
//                        var media_type = '<video controls src="'+ data.result.result.data[i].media_url +'"/>';
//                    }
                    if (data.result.result.data[i].media_type == 'VIDEO'){
//                    console.log("jhi all :11100777", data.result.result.data[i].media_type)
                        var media_type = '<video controls style="width: 100%;height: auto;" src="'+ data.result.result.data[i].media_url +'"/>';
                    }
                    if (data.result.result.data[i].media_type == 'IMAGE'){
                        var media_type = '<img class="img-fluid" src="' + data.result.result.data[i].media_url + '" />';
                    }
                    if (data.result.result.data[i].media_type == 'CAROUSEL_ALBUM'){
//                        console.log("jhi all laubum  :11100777", data.result.result.data[i].media_type)
                        var media_type = '<img class="img-fluid" src="' + data.result.result.data[i].media_url + '" />';
                    }
//                    var media_type = '<img class="img-fluid" src="' + data.result.result.data[i].media_url + '" />';
                    removedStr  = mesage.substring(maxLength, $.trim(mesage).length);
                  //  mesage=removedStr;
                    removedStrdict[data.result.result.data[i].id] = removedStr
                     //$for_data += '<div class="card border-0 mt-2"><div class="card-box-shadow"><div class="row p-2">'+ mesage+'</div></div></div>'; 
                     $for_data += '<div class="card border-0 mt-2"><div class="card-box-shadow">'+ media_type +'<div class="row"><div class="card-body pt-0"><div class="col-9 pl-0"><a class="d-block" href="http://www.instagram.com/">' + data.result.result.data[i].username + '</a><small class="text-muted">'+ current_date +'</small></div></div></div><p class="card-text p-3 text-secondary text show-more-height">'+ mesage+'</p></div><div class="card-body pb-4"><div class="card-post-icon text-secondary"></div><div class="share-post pt-sm-3 pt-2 mt-sm-3 mt-2 border-top"><div class="row"><div class="col-12 px-0 text-center"><a class="d-inline-block py-1 text-primary w-100" href="' + data.result.result.data[i].permalink + '" title="View on Instagram" target="_blank"><small>View on Instagram</small></a></div></div></div></div></div>';
                     //$for_data += '<div class="card border-0 mt-2"><div class="card-box-shadow"><div class="row p-2"><div class="card-img-top col-3 text-center"><img class="rounded-circle img-fluid" src="' + data.result.image_url.profile_picture_url + '" /></div><div class="card-body pt-0"><div class="col-9 pl-0"><a class="d-block" href="http://www.instagram.com/">' + data.result.result.data[i].username + '</a><small class="text-muted">'+ current_date +'</small></div></div></div><p class="card-text p-3 text-secondary text show-more-height">'+ mesage+'</p></div>'+ media_type +'<div class="card-body pb-4"><div class="card-post-icon text-secondary"><small class="pl-2"><i class="fa fa-heart"></i> ' +  data.result.result.data[i].like_count +' Likes</small><small class="px-1"><i class="fa fa-comments"></i> ' +  data.result.result.data[i].comments_count +' Comments</small></div><div class="share-post pt-sm-3 pt-2 mt-sm-3 mt-2 border-top"><div class="row"><div class="col-12 px-0 text-center"><a class="d-inline-block py-1 text-primary w-100" href="' + data.result.result.data[i].permalink + '" title="View on Instagram" target="_blank"><small>View on Instagram</small></a></div></div></div></div></div>';
                     //$for_data += '<div class="grid-item card border-0 mt-2"><div class="card card-box-shadow"><div class="card-body"><div class="row pb-sm-3 pb-2"><div class="card-img-top col-3 text-center"><img class="rounded-circle img-fluid" src="' + data.result.fb_image_url + '" /></div><div class="col-9 pl-0"><a class="d-block" href="http://www.facebook.com/' + data.result.fb_page_id + '">' + data.result.fb_result.posts.data[i].from.name + '</a><small class="text-muted">' + current_date + '</small></div></div><p class="card-text text-secondary more">' + message + '</p></div><img class="img-fluid" src="' + data.result.fb_result.posts.data[i].full_picture + '" /><div class="card-body pb-4"><div class="card-post-icon text-secondary"><img src="facebook_feed_axis/static/src/img/fb-like.png" /><img src="facebook_feed_axis/static/src/img/fb-heart-icon.png" /><img src="facebook_feed_axis/static/src/img/fb-emoji-icon.png" /><img src="facebook_feed_axis/static/src/img/emoji_icon2.png" /><img src="facebook_feed_axis/static/src/img/emoji_icon3.png" /><img src="facebook_feed_axis/static/src/img/emoji_icon4.png" /><small class="pl-2">' + likes_count.length + ' likes</small><small class="px-1">' + comments_count.length + ' comments</small></div><div class="share-post pt-sm-3 pt-2 mt-sm-3 mt-2 border-top"><div class="row"><div class="col-12 px-0 text-center"><a class="d-inline-block py-1 text-primary w-100" href="https://www.facebook.com/' + data.result.fb_result.posts.data[i].id + '" title="View on Facebook"><small>View on Facebook</small></a></div></div></div></div></div></div>';
                }
                $for_data += "</div>";
                // <div class="elipsetext" data-id='+ data.result.result.data[i].id +'>...Read More</div><div class="showless d-none" data-id='+ data.result.result.data[i].id +'>Read Less</div>
                // $(document).ready(function(){
                //     $('.elipsetext').click(function() {
                //         var id = $(this).attr("data-id");
                //         for(var key in removedStrdict) {
                //             if(key == id) {
                //                 var html = '<p class="more-text">'+ removedStrdict[key] +'</p>';
                //                 $(this).html(html);
                //                 $('.more-text').show();
                //                 $('.showless').removeClass('d-none');
                //                 // $('.elipsetext').addClass('d-none');
                //             }
                //         }
                //     });
                //     $('.showless').click(function() {
                //         var id = $(this).attr("data-id");
                //         for(var key in removedStrdict) {
                //             if(key == id) {
                //                 $('.more-text').hide();
                //                 $('.showless').addClass('d-none');
                //                 // $('.elipsetext').removeClass('d-none');
                //             }
                //         }
                        
                //     });
                    
                // })

                $('#instafeed').append($for_data);
                    // var $grid = $('.grid').masonry({
                    //     itemSelector: '.grid-item',
                    //     columnWidth: '.grid-sizer',
                    //     gutter: '.gutter-sizer',
                    //     horizontalOrder: true, // new!
                    //     percentPosition: true,
                    // });
                // $(document).ready(function() {
                //     $('div.msg_content').each(function(){
                //         var LiN = .length;
                //         console.log("=======lenght====", LiN)
                //     });
                // });

                if (data.result.result['paging']['next']) {
                        // $("#loadmore").show();
                }
                $("#page").val(1);
                $("#loadmore").on('click', function(e) {
                    /*i++;*/
                    var current_page_number = parseInt($("#page").val());
                    ajax.jsonRpc("/instagram_post_next", 'call', {
                        'page_number': current_page_number,
                    }).then(function(data) {
//                    console.log("11new to data:", data.result.data)
                        if(data){
                            var limit = data.result.data.length;
//                            var $for_data = "";
                            var $for_data = "<div class='card-columns'>";
                            for (var i = 0; i < limit; i++) {
//                                console.log("11new to data_type:", data.result.data[i].media_type)
                                var date = new Date(data.result.data[i].timestamp);
                                if (data.result.data[i].caption) {
                                     var mesage = data.result.data[i].caption;
                                } else {
                                    var mesage = '';
                                }
                                if (data.result.data[i].media_type === 'VIDEO'){
//                                    console.log("1If video tyepe:", data.result.data[i].media_type);
                                    var media_type = '<video style="width: 100%;height: auto;" controls src="'+ data.result.data[i].media_url +'"/>';
                                }
                               if (data.result.data[i].media_type == 'IMAGE'){
                                    var media_type = '<img class="img-fluid" src="' + data.result.data[i].media_url + '" />';
                                }
                                 if (data.result.data[i].media_type == 'CAROUSEL_ALBUM'){
                                    var media_type = '<img class="img-fluid" src="' + data.result.data[i].media_url + '" />';
//                                    var media_type = '<video style="width: 100%;height: auto;" controls src="'+ data.result.data[i].media_url +'"/>';
                                    }
                                $for_data += '<div class="card border-0 mt-2"><div class="card-box-shadow">'+ media_type +'<div class="row"><div class="card-body pt-0"><div class="col-9 pl-0"><a class="d-block" href="http://www.instagram.com/">' + data.result.data[i].username + '</a><small class="text-muted">'+ current_date +'</small></div></div></div><p class="card-text p-3 text-secondary text show-more-height">'+ mesage+'</p></div><div class="card-body pb-4"><div class="card-post-icon text-secondary"></div><div class="share-post pt-sm-3 pt-2 mt-sm-3 mt-2 border-top"><div class="row"><div class="col-12 px-0 text-center"><a class="d-inline-block py-1 text-primary w-100" href="' + data.result.data[i].permalink + '" title="View on Instagram" target="_blank"><small>View on Instagram</small></a></div></div></div></div></div>';
                                
//                                $for_data += '<div class="grid-item card border-0 mt-2"><div class="card-box-shadow"><div class="card-body"><div class="row pb-sm-3 pb-2"><div class="col-3 text-center"><img class="rounded-circle img-fluid" src="' + data.image_url.profile_picture_url + '" /></div><div class="col-9 pl-0"><a class="d-block" href="http://www.instagram.com/">' + data.result.data[i].username + '</a><small class="text-muted">' + date +'</small></div></div><div id="profile-description"><div class="text show-more-height"><p class="card-text p-3 text-secondary more">'+ mesage +'</p></div></div></div>'+ media_type +'<div class="card-body pb-4"><div class="card-post-icon text-secondary"><small class="pl-2">' +  data.result.data[i].like_count +' Likes</small><small class="px-1">' +  data.result.data[i].comments_count +' Comments</small></div><div class="share-post pt-sm-3 pt-2 mt-sm-3 mt-2 border-top"><div class="row"><div class="col-12 px-0 text-center"><a class="d-inline-block py-1 text-primary w-100" href="' + data.result.data[i].permalink + '" title="View on Instagram" target="_blank"><small>View on Instagram</small></a></div></div></div></div></div></div></br>';
                            }
                            $for_data += "</div>";
                            var $elems = $($for_data);
                            $('#instafeed').append($elems);
                            // $grid.append($elems).masonry('appended', $elems);
                            if (data.result['paging']['next']) {
                                $("#loadmore").show();
                            } else {
//                                $("#loadmore").attr("style",'display:none !important');
                            }
                            $("#page").val(current_page_number + 1)
                        }

                    });

                });
            }
        }else{
         $("#loadmore").attr("style",'display:none !important');
         }
        },
        error: function () {
            console.log("ERROR: <h2>Something went wrong in loading instagram post..</h2>");
        }
    });

 /*   var checkPosition = function() {
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

    };*/
    $(window).scroll(checkPosition);
    $(".show-more").click(function () {
        //console.log("------------------------show more")
        if($(".text").hasClass("show-more-height")) {
            $(this).text("(Show Less)");
        } else {
            $(this).text("(Show More)");
        }

        $(".text").toggleClass("show-more-height");
    });
});

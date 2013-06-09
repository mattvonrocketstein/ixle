// TODO: rename file to ixle_api.js

// TODO: move to base_js.js
function flash(msg){
    if( $('.flashes') ){
        var _id = 'flash_' + Math.floor(Math.random()*200);
        $('.flashes').append('<li id=' + _id + '>'+msg+'</li>');
        var x = $('#'+_id);
        var delay = 10000;
        x.fadeOut(delay);
        setTimeout(function() { x.remove() }, delay);

    }
    else{
        alert(msg);}
}
function handle_api_success(data){
    console.debug('raw api result:');
    console.debug(data);
    var data = eval(data);
    console.debug('interpretted api result:')
    console.debug(data);
    var ppTable = prettyPrint(data);
    $('#block_body').html('' + $(ppTable).html());
    if(data['error']){
        flash('ERROR: ' + data['error'])}
    else if(data['last_error']){
        console.debug('maybe good');
        console.debug(data);}
    else{
        console.debug('looks good')
        console.debug(data);
    }
    //if(data.redirect_to){
    //window.location=data.redirect_to}
}

function interstitial_api_call(api_name){
    var tmp = pdata(api_name);
    tmp['need_input']=1;
    return post_to_api(tmp)
}

function pdata(api_name, data){ // aggregate data for any kind of api post
    var out = data || {};
    out['cache'] = (new Date()).getTime()+'';
    out['action'] = api_name;
    out['_'] = {{_|escapejs}}
    return out;
}
function post_to_api(api_name, post_data){
    var tmp = post_data || pdata(api_name);
    flash('posting to api@' + api_name);
    var answer = confirm("post \"{{_}}\" to api @ " + api_name)
    if (answer){
        $.ajax({type : 'GET',
                url : '/api',
                data :  tmp})
            .success(handle_api_success)
            .fail(function(data){
                console.debug(data);
                flash('ERROR: ' + data)});
    }
    else{
        flash("canceled posting to api");
    }
}

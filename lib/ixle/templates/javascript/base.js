function move_file_to_dir(f,d){
    console.debug("moving "+f+" to "+d);
    post_and_redirect('/move_file', {file:f, dir:d});
}

function copyToClipboard (text) {
  window.prompt ("Copy to clipboard: Ctrl+C, Enter", text);
}
copy2clipboard=copyToClipboard
function path2clipboard(){
    window.prompt("Copy to clipboard: Ctrl+C, Enter",
                 "{{_|default("nothing to copy")}}");
}

function json2string(obj){
    return JSON.stringify(obj, undefined, 2)
}

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
//{# due to form encoding, this wont work with filenames including commas #}
post_and_redirect=$().redirect

function json2html(data, container){
    $('#'+container).html(prettyPrint(data));
}

function json2form(data, container){
}

$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};
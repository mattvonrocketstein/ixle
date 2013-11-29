function copyToClipboard (text) {
  window.prompt ("Copy to clipboard: Ctrl+C, Enter", text);
}
copy2clipboard=copyToClipboard

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

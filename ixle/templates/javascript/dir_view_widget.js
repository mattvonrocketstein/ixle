$(document).ready(function(){
    $('#dir_view_widget').load('/dir_view_widget', {'_':{{abspath|escapejs}},'is_dir':'{{is_dir}}'});
});

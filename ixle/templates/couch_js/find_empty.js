function(doc){
    if( null==doc.{{fieldname}} || doc.{{fieldname}}.length==0 ){
        emit(doc._id, doc)
    }
}
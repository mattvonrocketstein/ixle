function(doc){
    if( doc['{{fieldname}}']=='{{value}}'){
        emit(doc.id, null)
    }
}
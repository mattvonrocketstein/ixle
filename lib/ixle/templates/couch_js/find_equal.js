function(doc){
    if( doc['{{fieldname}}']=='{{value}}' ){
        emit(doc._id, doc)
    }
}
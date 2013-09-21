function(doc){
    if (doc['path'].substring(0, '{{substring}}'.length) === '{{substring}}'){
        emit(doc._id, doc)
    }
}
function(doc){
    if (doc._id.substring(0, '{{substring}}'.length) === '{{substring}}'){
        emit(doc.id, doc)
    }
}
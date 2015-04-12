function(doc) {

  if (doc.type == "seed") {
      emit(doc._id, doc);
  }
  
}

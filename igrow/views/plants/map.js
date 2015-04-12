function(doc) {
  
	if (doc.type == "seed") {
		emit(doc.common_name, 1);
	}
	
}
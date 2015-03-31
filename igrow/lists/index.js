function (head, req) {
  var ddoc = this;
  var Mustache = require("lib/mustache");
  var List = require("vendor/couchapp/lib/list");
  var path = require("vendor/couchapp/lib/path").init(req);
  var Atom = require("vendor/couchapp/lib/atom");

  var indexPath = path.list('index','recent-seeds',{descending:true, limit:10});
  var feedPath = path.list('index','recent-seeds',{descending:true, limit:10, format:"atom"});
  var commentsFeed = path.list('comments','comments',{descending:true, limit:10, format:"atom"});

  var path_parts = req.path;
  // The provides function serves the format the client requests.
  // The first matching format is sent, so reordering functions changes 
  // thier priority. In this case HTML is the preferred format, so it comes first.
  provides("html", function() {
    var key = "";
    // render the html head using a template
    var stash = {
      header : {
        index : indexPath,
        igrowName : ddoc.igrow.title,
        feedPath : feedPath,
        commentsFeed : commentsFeed
      },
      scripts : {},
      db : req.path[0],
      design : req.path[2],
      feedPath : feedPath,
      sidebar : {
        seedPath : path.show("seed")+"/",
        sowingPath : path.show("sowing")+"/",
        pottingPath : path.show("potting")+"/",
        labelsPath : path.list("labels")+"/"
      },
      assets : path.asset(),
      recentseeds : List.withRows(function(row) {
        var seed = row.value;
        key = row.key;
        return {
          common_name : seed.common_name,
          variety_or_cultivar : seed.variety_or_cultivar,
          variety_url : seed.variety_url,
          supplier : seed.supplier,
          pack_size : seed.pack_size,
          price : seed.price,
          created : seed.created,
          user : seed.user,
          link : path.list('seed','seed-page', {startkey : [row.id]})
        };
      }),
      older : function() {
        return path.older(key);
      },
      "5" : path.limit(5),
      "10" : path.limit(10),
      "25" : path.limit(25)
    };
    return Mustache.to_html(ddoc.templates.index, stash, ddoc.templates.partials, List.send);
  });

  // if the client requests an atom feed and not html, 
  // we run this function to generate the feed.
  provides("atom", function() {    
    var path = require("vendor/couchapp/lib/path").init(req);
    var markdown = require("vendor/couchapp/lib/markdown");
    var textile = require("vendor/textile/textile");

    // we load the first row to find the most recent change date
    var row = getRow();
    
    // generate the feed header
    var feedHeader = Atom.header({
      updated : (row ? new Date(row.value.created_at) : new Date()),
      title : ddoc.igrow.title,
      feed_id : path.absolute(indexPath),
      feed_link : path.absolute(feedPath),
    });
    
    // send the header to the client
    send(feedHeader);

    // loop over all rows
    if (row) {
      do {
        if (row.value.format == "markdown") {
          var html = markdown.encode(row.value.body);
        } else if (row.value.format == "textile") {
          var html = textile.encode(row.value.body);
        } else {
          var html = Mustache.escape(row.value.html);
        }
        // generate the entry for this row
        var feedEntry = Atom.entry({
          entry_id : path.absolute('/'+encodeURIComponent(req.info.db_name)+'/'+encodeURIComponent(row.id)),
          title : row.value.title,
          content : html,
          updated : new Date(row.value.created_at),
          author : row.value.author,
          alternate : path.absolute(path.show('post', row.id))
        });
        // send the entry to client
        send(feedEntry);
      } while (row = getRow());
    }

    // close the loop after all rows are rendered
    return "</feed>";
  });
};
var base_fn = function(ticks,i) {
    return ticks.append("svg:image")
        .attr("xlink:href","/img/link.png")
        .attr("width", 18)
        .attr("height",18)
        .attr("x", -margin.left + 5 + (i*20))
        .attr("y", -9);
}

var icon_fns = {"link" : function(ticks, i) {
      base_fn(ticks,i)
        .attr("xlink:href","/img/link.png")
        .attr("class", "linkIcon icon")
        .on("click", function(d) { window.location.href = window.location.origin + window.location.pathname + "?doc=" + encodeURIComponent(d);});
  },
 "ap" : function(ticks, i) {
      base_fn(ticks,i)
        .attr("data-doc-id", function (d) {return d})
        .attr("xlink:href","/img/ap.jpg")
        .attr("class", "apIcon icon")
        .attr("onclick", function(d) { return (d) ? "fulltext.popover(this)" : ""; });
  },
 "fulltext-jeff" : function(ticks, i,docs) {
      base_fn(ticks,i)
        .attr("data-doc-id", function (d) {return d})
        .attr("data-doc-label", function (d) {
          data = docs.filter(function(doc, i) { return doc.id == d})[0];
            try {
              return data.label;
            } catch (e) {
              return d;  
            }; 
          })
        .attr("xlink:href","/img/icon-book.png")
        .attr("class", "fulltextIcon icon")
        .attr("onclick", function(d) { 
          data = docs.filter(function(doc, i) { return doc.id == d})[0];
          if (data.label.startsWith("BOOK")) { 
            id = data.id.replace(".txt","");
            url = "http://babel.hathitrust.org/cgi/pt?id={0}".format(id);
            return "window.open('{0}', '_blank')".format(url);
          } else
            return (d) ? "fulltext.popover(this)" : ""; 
        });
  },
 "fulltext-inline" : function(ticks, i,docs) {
      base_fn(ticks,i)
        .attr("data-doc-id", function (d) {return d})
        .attr("data-doc-label", function (d) {
          data = docs.filter(function(doc, i) { return doc.id == d})[0];
            try {
              return data.label;
            } catch (e) {
              return d;  
            }; 
          })
        .attr("xlink:href","/img/icon-book.png")
        .attr("class", "fulltextIcon icon")
        .attr("onclick", function(d) { return (d) ? "fulltext.popover(this)" : ""; });
  },
 "fulltext" : function(ticks, i,docs) {
      base_fn(ticks,i)
        .attr("data-doc-id", function (d) {return d})
        .attr("xlink:href","/img/icon-book.png")
        .attr("class", "fulltextIcon icon")
        .on("click", function(d){
          var url = window.location.origin + window.location.pathname + "../fulltext/" + encodeURIComponent(d);
          window.open(url);
        }).append("title").text(function (d) { "Fulltext view of " + d });
  },
 "oldbailey" : function(ticks, i, docs) {
      base_fn(ticks,i)
        .attr("data-doc-id", function (d) {return d})
        .attr("xlink:href","/img/icon-law.png")
        .attr("class", "oldbaileyIcon icon")
        .on("click", function(d) { 
          data = docs.filter(function(doc, i) { return doc.id == d})[0];
          d = data.metadata.trial_id;
          window.open("http://www.oldbaileyonline.org/browse.jsp?id="+d+"&div="+d, "_blank");
        });
  },
 "htrc" : function(ticks, i, docs) {
      base_fn(ticks,i)
        .attr("xlink:href","/img/htrc.png")
        .attr("class", "htrcIcon icon")
        .attr("data-htrc-page", function(d) { 
          if (Number(d) == NaN)
            return '';
          else {
            data = docs.filter(function(doc, i) { return doc.id == d})[0]
            try {
              return data.metadata.seq_number
            } catch (e) {
              return '';  
            }; 
          }})
        .attr("data-htrc-id", function(d) { 
          data = docs.filter(function(doc, i) { return doc.id == d})[0]
          return data.metadata.book_label; 
        })
        .attr("onclick", function(d) { return (d) ? "htrc.popover(this)" : ""; });
  },
 "htrcbook" : function(ticks, i, docs) {
      base_fn(ticks,i)
        .attr("xlink:href","/img/icon-book.png")
        .attr("class", "htrcbookIcon icon")
        .on("click", function(d) { 
          data = docs.filter(function(doc, i) { return doc.id == d})[0]
          id = data.metadata.book_label;
          page = data.metadata.seq_number;
          url = "http://babel.hathitrust.org/cgi/pt?id={0};seq={1}".format(id, page)
          window.open(url, "_blank");});
  },
 "doi" : function(ticks, i, docs) {
      base_fn(ticks,i)
        .attr("xlink:href","/img/icon-doi.png")
        .attr("class", "doiIcon icon")
        .on("click", function(d) { 
          data = docs.filter(function(doc, i) { return doc.id == d})[0]
          doi = data.metadata.doi;
          url = "http://dx.doi.org/{0}".format(doi)
          window.open(url, "_blank");});
  },
 "wos" : function(ticks, i, docs) {
      base_fn(ticks,i)
        .attr("xlink:href","/img/icon-wos.png")
        .attr("class", "wosIcon icon")
        .on("click", function(d) { window.open("http://apps.webofknowledge.com/CitedFullRecord.do?product=WOS&search_mode=CitedFullRecord&isickref=" + d, "_blank");});
  },
 "inpho" : function(ticks, i) { 
      base_fn(ticks,i)
        .attr("xlink:href","/img/inpho.png")
        .attr("class", "inphoIcon icon")
        .on("click", function(d) { window.open("https://inpho.cogs.indiana.edu/entity?redirect=True&sep=" + d, "_blank");});
   },
 "sep" : function(ticks, i) {
      base_fn(ticks,i)
        .attr("xlink:href","/img/sep.png")
        .attr("class", "sepIcon icon")
        .on("click", function(d) { window.open("http://plato.stanford.edu/entries/" + d, "_blank");});
   }
};

String.prototype.format = String.prototype.f = function() {
    var s = this,
        i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

var icon_tooltips = {
    "link" : 'Click to refocus the Topic Explorer on this document.',
    "ap" : 'Click for the full-text.',
    "fulltext" : 'Click for the full-text.',
    "oldbailey" : 'Click to open Old Bailey Online Record.',
    "htrc" : 'Click for the HathiTrust Details.',
    "htrcbook" : 'Click for the HathiTrust PageTurner.',
    "inpho" : 'Click to see more information<br /> at the InPhO Project.',
    "sep" : 'Click for the SEP article.',
    "doi" : 'Click to lookup the article by DOI.',
    "wos" : "Click to open the Thomson Reuters Web of Science record."
    };

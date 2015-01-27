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
        .on("click", function(d) { window.location.href = "/?doc=" + encodeURIComponent(d);});
  },
 "ap" : function(ticks, i) {
      base_fn(ticks,i)
        .attr("data-doc-id", function (d) {return d})
        .attr("xlink:href","/img/ap.jpg")
        .attr("class", "apIcon icon")
        .attr("onclick", function(d) { return (d) ? "fulltext.popover(this)" : ""; });
  },
 "fulltext" : function(ticks, i) {
      base_fn(ticks,i)
        .attr("data-doc-id", function (d) {return d})
        .attr("xlink:href","/img/icon-book.png")
        .attr("class", "fulltextIcon icon")
        .attr("onclick", function(d) { return (d) ? "fulltext.popover(this)" : ""; });
  },
 "htrc" : function(ticks, i) {
      base_fn(ticks,i)
        .attr("xlink:href","/img/htrc.png")
        .attr("class", "htrcIcon icon")
        .attr("data-htrc-id", function(d) { return d; })
        .attr("onclick", function(d) { return (d) ? "htrc.popover(this)" : ""; });
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
        .on("click", function(d) { window.open("http://plato.stanford.edu/entires/" + d, "_blank");});
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
    "htrc" : 'Click for the HathiTrust Details.',
    "inpho" : 'Click to see more information<br /> at the InPhO Project.',
    "sep" : 'Click for the SEP article.'
    };

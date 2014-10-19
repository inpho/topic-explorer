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
        .attr("class", "linkIcon")
        .on("click", function(d) { window.location.href = "/?doc=" + encodeURIComponent(d);});
  },
 "ap" : function(ticks, i) {
      base_fn(ticks,i)
        .attr("data-doc-id", function (d) {return d})
        .attr("xlink:href","/img/ap.jpg")
        .attr("class", "apIcon")
        .attr("onclick", function(d) { return (d) ? "ap.popover(this)" : ""; });
   
  },
 "htrc" : function(ticks, i) {
      base_fn(ticks,i)
        .attr("xlink:href","/img/htrc.png")
        .attr("class", "htrcIcon")
        .attr("data-htrc-id", function(d) { return d; })
        .attr("onclick", function(d) { return (d) ? "htrc.popover(this)" : ""; });
  },
 "inpho" : function(ticks, i) { 
      base_fn(ticks,i)
        .attr("xlink:href","/img/inpho.png")
        .attr("class", "inphoIcon")
        .on("click", function(d) { window.open("https://inpho.cogs.indiana.edu/entity?redirect=True&sep=" + d, "_blank");});
   },
 "sep" : function(ticks, i) {
      base_fn(ticks,i)
        .attr("xlink:href","/img/sep.png")
        .attr("class", "sepIcon")
        .on("click", function(d) { window.open("http://plato.stanford.edu/entires/" + d, "_blank");});
   }
};

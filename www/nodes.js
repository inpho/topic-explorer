var q = inpho.util.getValueForURLParam('q') || null;
if (q) {
  q = decodeURIComponent(q);
  q = q.split('+').join(' ');
  $('#words').val(q);
  $('#words').css('font-weight', 'bold');
  $('#words').change(function() {
    $('#words').css('font-weight', 'normal');
  });
};

if (window.location.pathname.endsWith('topics') || window.location.pathname.endsWith('topics.local.html')) {
  var i = window.location.pathname.lastIndexOf('topics');
  var base_url = window.location.origin + window.location.pathname.substr(0,i);
} else {
  var base_url = window.location.origin + window.location.pathname;
}

var combineWords = function(words) {
  return d3.keys(words).sort(function(a,b) {
    if (words[a] > words[b])
      return -1;
    else if (words[a] < words[b])
      return 1;
    else
      return 0;
  }).join(", ") + ", ..."; 
}



var margin = {top: 20, right: 80, bottom: 80, left: 40},
  width = $('#chart').parent().width() - margin.left - margin.right,
  height = $(document).height() - Math.min($('#main').height(), 400) - margin.top - margin.bottom,
  padding = 1, // separation between nodes
  radius = 30;

var x = d3.scale.linear()
  .range([0, width]);

var y = d3.scale.linear()
  .range([height, 0]);

var color = d3.scale.category20();

var opacity = d3.scale.linear()
  .range([1.0, 0.0]);


var xAxis = d3.svg.axis()
  .scale(x)
  .orient("bottom");

var yAxis = d3.svg.axis()
  .scale(y)
  .orient("left");

var controls = d3.select("#chart").append("label")
  .attr("id", "controls")
  .attr("class", "hide");
var checkbox = controls.append("input")
  .attr("id", "collisiondetection")
  .attr("type", "checkbox");
controls.append("span")
  .text("Collision detection");

var svg = d3.select("#chart").append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

$(document).ready(function() {
  $.ajaxSetup({ cache: true });
});

var ext_data;

d3.csv(base_url + "cluster.csv", function(error, data) {
  var topics = {}; var node;
  var ks = data.map(function(d) { return parseInt(d.k); }).filter(function(item, i, ar){ return ar.indexOf(item) === i; });;

  // sidebar items
  var cluster_view = $('#sidebar-topics li:first-child').html();
  $('#sidebar-topics').html('');
  if (!window.location.pathname.endsWith('topics.local.html'))
    $('#sidebar-topics').append('<li>' + cluster_view + "</li>");
  ks.map(function(k) { $('#sidebar-topics').append('<li><a class="bg-info" title="Toggle '+k+'-topic clusters" data-placement="right" href="javascript:toggleDisplay(' + k + ')">' + k + '</a></li>') });
  $('#sidebar-topics li a').tooltip();

  var sizes = d3.scale.linear()
    .range([radius, 5]);
  sizes.domain(d3.extent(ks)).nice();

  ext_data = data;
  var xVar = "orig_x",
      yVar = "orig_y";

  data.forEach(function(d) {
    d[xVar] = parseFloat(d[xVar]);
    d[yVar] = parseFloat(d[yVar]);
  });

  var force = d3.layout.force()
    .nodes(data)
    .size([width, height])
    .on("tick", tick)
    .charge(-1)
    .gravity(0);
    //.chargeDistance(20);

  x.domain(d3.extent(data, function(d) { return d[xVar]; })).nice();
  y.domain(d3.extent(data, function(d) { return d[yVar]; })).nice();

  var prev = data[0].k;
  var currentTop = 0;
  // Set initial positions
  data.forEach(function(d) {
    d.x = x(d[xVar]);
    d.y = y(d[yVar]);
    d.color = color(d.cluster);
    d.radius = sizes(d.k);
    if (d.k != prev) { prev = d.k; currentTop = 0; }
    d.topic = currentTop++;
  });

  $('#chart #loading').remove();
  controls.attr('class', '')

  /*
  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);
      */
  /*
    .append("text")
      .attr("class", "label")
      .attr("x", width)
      .attr("y", -6)
      .style("text-anchor", "end")
      .text("Sepal Width (cm)");*/
/*
  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis);
      */
  /*
    .append("text")
      .attr("class", "label")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Sepal Length (cm)");*/
  


  var k_urls = ks.map(function(k) { return base_url + k + "/topics.json" });
  console.log(ks, k_urls);
  Promise.all(k_urls.map($.getJSON)).then(function (data) {
      data.forEach(function(d,i) {
        topics[ks[i]] = $.each(d, function(key, val) { d[key] = combineWords(val.words) });
      });
    }).then(function() {
      var words = inpho.util.getValueForURLParam('q');
      return (words) ? $.getJSON('topics.json?q=' + words) : null })
    .catch(function(error) {
      var words = inpho.util.getValueForURLParam('q');
      if (error.status == 404) {
        $('#words').parents('.form-group').addClass('has-error');
        $('#words').attr('placeholder', 'Terms not in corpus: "' + words + '". Try another query...');
        $('#words').val('');
      } else if (error.status == 410) { 
        $('#words').parents('.form-group').addClass('has-warning');
        $('#words').attr('placeholder', 'Terms removed by stoplisting: "' + words + '". Try another query...');
        $('#words').val('');
      }
    }).then(function(distData) {
      if (distData != null) {
          $('#words').parents('.form-group').removeClass('has-error');
          $('#words').parents('.form-group').removeClass('has-warning');
          $('#words').parents('.form-group').addClass('has-success');
          opacity.domain(d3.extent(distData, function(d) { return d['distance']; })).nice();
          for (var obj in distData) {
            obj = distData[obj];
            data.map(function(d) { if (d.k == obj.k.toString() && d.topic == obj.t) d.opacity = obj.distance; });
          }
      }
    }).then(function() {
      console.log(data); 
      node = svg.selectAll(".dot")
          .data(data, function(d) { return d.k + '-' + d.topic; })
        .enter().append("circle")
          .attr("class", "dot")
          .attr("r", function(d) { return d.radius; })
          .attr("cx", function(d) { return x(d[xVar]); })
          .attr("cy", function(d) { return y(d[yVar]); })
          //.attr("style", function(d) { return "fill:" + d.color +"; fill-opacity: "+ opacity(d.opacity) + ";"; })
          .style("fill", function(d) { return d.color; })
          .style("fill-opacity", function(d) { return opacity(d.opacity) || 0.7; })
          .on("click", function(d) { window.location.href = base_url + d.k + "/?topic=" + d.topic })
          .attr("title", function(d) {
            return "<strong>Topic " + d.topic + "</strong> (k=" + d.k + ")"
              + "<br />" + topics[d.k][d.topic];
          })
        .on("mouseover", function (d) { $(this).tooltip('show')})
        .on("mouseout", function (d) { $(this).tooltip('hide')});
      
      $(".dot").tooltip({container:'body', trigger: 'manual', animation: false, html: true});

  });
/*
  var legend = svg.selectAll(".legend")
      .data(color.domain())
    .enter().append("g")
      .attr("class", "legend")
      .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

  legend.append("rect")
      .attr("x", width - 18)
      .attr("width", 18)
      .attr("height", 18)
      .style("fill", color);

  legend.append("text")
      .attr("x", width - 24)
      .attr("y", 9)
      .attr("dy", ".35em")
      .style("text-anchor", "end")
      .text(function(d) { return d; });
*/
  d3.select("#collisiondetection").on("change", function() {
    if (!checkbox.node().checked)
      force    
        .charge(0)
        .gravity(0)
        //.chargeDistance(0)
        .start();
    else
      force    
        .charge(-1)
        .gravity(0)
        //.chargeDistance(20)
        .start();

  });

  function tick(e) {
    node.each(moveTowardDataPosition(e.alpha));

    if (checkbox.node().checked) node.each(collide(e.alpha));

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
  }

  function moveTowardDataPosition(alpha) {
    return function(d) {
      d.x += (x(d[xVar]) - d.x) * 0.1 * alpha;
      d.y += (y(d[yVar]) - d.y) * 0.1 * alpha;
    };
  }

  // Resolve collisions between nodes.
  function collide(alpha) {
    var quadtree = d3.geom.quadtree(data);
    return function(d) {
      var r = d.radius + radius + padding,
          nx1 = d.x - r,
          nx2 = d.x + r,
          ny1 = d.y - r,
          ny2 = d.y + r;
      quadtree.visit(function(quad, x1, y1, x2, y2) {
        if (quad.point && (quad.point !== d)) {
          var x = d.x - quad.point.x,
              y = d.y - quad.point.y,
              l = Math.sqrt(x * x + y * y),
              r = d.radius + quad.point.radius + (d.color !== quad.point.color) * padding;
          if (l < r) {
            l = (l - r) / l * alpha;
            d.x -= x *= l;
            d.y -= y *= l;
            quad.point.x += x;
            quad.point.y += y;
          }
        }
        return x1 > nx2 || x2 < nx1 || y1 > ny2 || y2 < ny1;
      });
    };
  }
});

var toggleDisplay = function(k) {
  var selection =  d3.selectAll(".dot").filter(function(d) { return d.k.toString() == k.toString() });
  console.log(selection);

  if (selection.style('display') == 'none') {
    selection.style('display', 'inline');
    $('.sidebar-nav li a')
      .filter(function() { return $(this).text() == k.toString() })
        .addClass('bg-info');
  } else {
    selection.style('display', 'none');
    $('.sidebar-nav li a')
      .filter(function() { return $(this).text() == k.toString() })
        .removeClass('bg-info');
  }
}

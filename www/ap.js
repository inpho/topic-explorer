var ap = ap || {};

/* htrc.popover
 * Create a popover for HTRC content
 * */
ap.popover = function(elt) {
  console.log("click the popover");
  if (!($(elt).data('popover'))) {
    var docid = $(elt).data('doc-id');
    $.get('/docs/'+docid+'.txt', function (data) {
      $(elt).popover({
        html: true,
        content : data,
        title : docid,
        container : 'body'
      });
     
     // append close button to title.
     var title = $(elt).data('popover').options.title;
     $(elt).data('popover').options.title = '<button type="button" class="close" data-dismiss="popover">&times;</button>' + title;
     $(elt).data('popover').tip()
        .on('click', '[data-dismiss="popover"]', function(e) { $(elt).popover('hide'); })
        .css({maxWidth: "640px", zIndex: '1100'});

     // manually show popover, instead of just initialize
     $(elt).popover('show');
    });
  }
}

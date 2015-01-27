var fulltext = fulltext || {};

/* htrc.popover
 * Create a popover for HTRC content
 * */
fulltext.popover = function(elt) {
  if (!($(elt).data('popover'))) {
    var docid = $(elt).data('doc-id');
    $.get('/fulltext/'+docid, function (data) {
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

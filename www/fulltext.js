// BOOTSTRAP.Modal class
// https://gist.github.com/cecilemuller/6147729

(function() {
  "use strict";

  /**
   * @namespace
   */
  var BOOTSTRAP = {};


  /**
   * Event types that `BOOTSTRAP.Modal.events` might send.
   * @readonly
   * @enum {string}
   * @property {string}  MODAL_SHOW   - This event fires immediately when the show instance method is called.
   * @property {string}  MODAL_SHOWN    - This event is fired when the modal has been made visible to the user (will wait for css transitions to complete).
   * @property {string}  MODAL_HIDE   - This event is fired immediately when the hide instance method has been called.
   * @property {string}  MODAL_HIDDEN   - This event is fired when the modal has finished being hidden from the user (will wait for css transitions to complete).
   * @property {string}  MODAL_CONFIRM  - This event fires when the modal is closed using the primary button.
   */
  BOOTSTRAP.EVENTS = {
    MODAL_SHOW: 'show',
    MODAL_SHOWN: 'shown',
    MODAL_HIDE: 'hide',
    MODAL_HIDDEN: 'hidden',
    MODAL_CONFIRM: 'BOOTSTRAP.EVENTS.MODAL_CONFIRM'
  };


  /**
   * Dynamically-created modal window.
   * @class
   * @member {String}  title        - Text shown in the header of the modal.
   * @member {String}  body       - Text shown in the body of the modal.
   * @member {Array}   steps        - Defines the steps of a multistep modal.
   * @member {string}  status       - Muted status text.
   * @member {string}  submit       - Label of the primary button.
   * @member {string}  cancel       - Label of the cancel button.
   * @member {string}  events       - jQuery reference to the container.
   * @constructor
   */
   BOOTSTRAP.Modal = function(data){
    if (typeof data === 'undefined') data = {};

    this.title = (typeof data.title === 'undefined') ? false : data.title;
    this.body = (typeof data.body === 'undefined') ? false : data.body;

    this.step_ids = [];
    this.steps = (typeof data.steps === 'undefined') ? false : data.steps;  

    this.status = (typeof data.status === 'undefined') ? false : data.status;
    this.submit = (typeof data.submit === 'undefined') ? false : data.submit;
    this.cancel = (typeof data.cancel === 'undefined') ? false : data.cancel;
    this.url = (typeof data.url === 'undefined') ? false : data.url;
    this.close = (typeof data.close === 'undefined') ? false : data.close;

    var html = '<div class="modal hide fade" tabindex="-1" role="dialog" aria-hidden="true">';
    if (this.title || this.cancel){
      html += '<div class="modal-header">';
      if (this.cancel) html += '<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>';
      if (this.title) html += '<h3>' + this.title + '</h3>';
      html += '</div>';
    }
    html += '<div class="modal-body">';
    if (this.steps){
      var step_ids = [];
      var l = this.steps.length;
      html += '<ol>';
      for (var i = 0; i < l; i++){
        var step = this.steps[i];
        html += '<li class="muted">';
        if (step.title) html += '<p>' + step.title + '</p>';
        if (step.percents || (step.percents === 0)) html += '<div class="progress progress-striped ' + (step.percents > 0 ? '' : 'hidden') + '"><div class="bar" style="width: ' + Math.max(0.5, step.percents) + '%;"></div></div>';
        html += '</li>';
        step_ids.push(step.id);
      }
      html += '</ol>';
      this.step_ids = step_ids;
    }
    html += '</div>';
    
    if (this.status){
      html += '<div class="modal-footer modal-status muted"><p>' + this.status + '</p></div>';
    }
    if (this.submit || this.cancel){
      html += '<div class="modal-footer">';
      if (this.cancel) html += '<button class="btn" data-dismiss="modal" aria-hidden="true">' + this.cancel + '</button>';
      //if (this.url) html += '<a target="_blank" class="btn" data-dismiss="modal" aria-hidden="true" href="'+this.url+'" >Open in new tab</a>';
      if (this.submit) html += '<button class="btn btn-primary btn-submit">' + this.submit + '</button>';
      html += '</div>';
    }
    html += '</div>';

    var options = {"show": false};
    if (this.close){
      options.keyboard = true;
    } else {
      options.keyboard = false;
      options.backdrop = 'static';
    }

    var $container = $(html);
    if (this.submit){
      $container.find('.btn-submit').on('click', $.proxy(function(){
        this.events.trigger(BOOTSTRAP.EVENTS.MODAL_CONFIRM);
        this.hide();
      }, this));
    }
    $container.modal(options);
    this.events = $container.appendTo('body');

    if (this.body) $('.modal-body', $container).append('<p>' + this.body + '</p>');

    this.$li = false;
    this.$progress = false;
    this.$bar = false;
  };


  /**
   * Changes the status text shown in the footer.
   * @param {String}  text      - Text to display
   */
  BOOTSTRAP.Modal.prototype.updateStatus = function(text){
    if (text === false){
      this.events.find('.modal-status').remove();
    } else if (this.status === false){
      this.events.find('.modal-body').after('<div class="modal-footer modal-status muted"><p>' + text + '</p></div>');
    } else {
      this.events.find('.modal-status p').html(text);
    }
    this.status = text;
  };
  

  /**
   * Opens the modal.
   */
  BOOTSTRAP.Modal.prototype.show = function(){
    this.events.modal('show');
  };


  /**
   * Closes the modal.
   */
  BOOTSTRAP.Modal.prototype.hide = function(){
    this.events.modal('hide');
  };


  /**
   * Opens the modal if it's closed, closes it if it's open.
   */
  BOOTSTRAP.Modal.prototype.toggle = function(){
    this.events.modal('toggle');
  };


  /**
   * Sets the active step (multistep modals only).
   * @param {String}  step_id     - Unique identifier of the step
   */
  BOOTSTRAP.Modal.prototype.startStep = function(step_id){
    var index = this.step_ids.indexOf(step_id);
    if (index > -1){
      this.$li = this.events.find('li:nth-of-type(' + (index + 1) + ')').removeClass('muted').addClass('text-info');
      this.$progress = this.$li.find('.progress').fadeIn('slow').addClass('active').removeClass('hidden');
      this.$bar = this.$li.find('.bar');
      return true;
    } else {
      return false;
    }
  };


  /**
   * Changes the percentage of the current step (multistep modals only).
   * @param {Number}  percents      - Width of the colored part of the progress bar of the current step, if it has one.
   */
  BOOTSTRAP.Modal.prototype.updateStep = function(percents){
    if (this.$bar){
      this.$bar.css('width', percents + '%');
      return true;
    } else {
      return false;
    }
  };


  /**
   * Sets the current step as failed (multistep modals only).
   * @param {String}  text      - Text to display
   */
  BOOTSTRAP.Modal.prototype.failStep = function(text){
    if (this.$li){
      this.$li.removeClass('text-info').addClass('text-error');
      this.$progress.remove();
      this.$li.append('<div class="alert alert-error">' + text + '</div>');
      this.$li = this.$bar = this.$progress = false;
      return true;
    } else {
      return false;
    }
  };


  /**
   * Sets the current step as successfully completed (multistep modals only).
   */
  BOOTSTRAP.Modal.prototype.completeStep = function(){
    if (this.$li){
      this.$li.removeClass('text-info').addClass('text-success');
      this.$bar.css('width', '100%').addClass('bar-success');
      this.$progress.removeClass('active');
      this.$li = this.$bar = this.$progress = false;
      return true;
    } else {
      return false;
    }
  };


  window['BOOTSTRAP'] = BOOTSTRAP;

})();

String.prototype.replaceAll = function(search, replace)
{
    //if replace is null, return original string otherwise it will
    //replace search string with 'undefined'.
    if(!replace) 
        return this;

    return this.replace(new RegExp('[' + search + ']', 'g'), replace);
};


var fulltext = fulltext || {};

fulltext.popover = function(elt) {
  if (!($(elt).data('modal'))) {
    var docid = $(elt).data('doc-id');
    var doclabel = $(elt).data('doc-label');
    $.get('../fulltext/'+encodeURIComponent(docid), function (data) {

  var mymodal = new BOOTSTRAP.Modal({
"title": doclabel,
"body":  $('<div>').text(data).html().replaceAll('\n','<br />'),
"status" : docid,
"submit": 'Close',
"cancel" : false,
"url" : '../fulltext/'+encodeURIComponent(docid),
"close" : true

});
    mymodal.show()
    });
  }
}

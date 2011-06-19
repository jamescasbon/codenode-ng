// Top level object to hold our app, also inits the main controller
var App = {
    
    // we can support 16 inserts before the position index needs rebalancing
    PositionGap: Math.pow(2,16), 
    Models: {},
    Views: {},
    Controllers: {},
    Collections: {},
    init: function() {
        new App.Controllers.Notebooks();
        Backbone.history.start();
    }
};

function scrollTo(selector) {
    var targetOffset = $(selector).offset().top - 100; // header
    $('html,body').animate({scrollTop: targetOffset}, 400);
}

function checkIfInView(element){
    //http://stackoverflow.com/questions/6215779/jquery-scroll-if-element-is-not-visible
    var offset = $(element).offset().top - $(window).scrollTop();
    console.log(offset + ' '  +  (window.innerHeight- $(element).height() ));
    if(offset > window.innerHeight - $(element).height() || offset < 0){
        // Not in view so scroll to it
        $('html,body').animate({scrollTop: offset}, 400);
        return false;
    }
   return true;
}


$(window).keydown(function(e) {
    if (e.keyCode === 8 & e.target.id != 'changetitle')
    {
        return false;
    }
});

App.Models.Cell = Backbone.Model.extend({
    initialize: function() {
        _.bindAll(this, 'evalSuccess');
    },
    
    // url: '/cells'
    evaluate: function(content, onfinish) {
        // TODO: callback for focus on output?
        console.log('App.Models.Cell.evaluate')
        
        if (this.get('mode') == 'text') {
            var converter = new Showdown.converter();
            var html = converter.makeHtml(content);
            this.set({
                'input': content,
                'output': html
            });
            onfinish();
            this.save();
        };
        if (this.get('mode') == 'code') {
            this.set({'input': content});
            window.notebook.engineEvaluate(content, this.evalSuccess(onfinish));
        };
        
    },
    
    evalSuccess: function(onfinish) { 
        var cell = this;
        return function(result) {
            cell.set({'output': result['result']});
            onfinish();
            cell.save();
        }
    },
    
    addAfter: function(collection) {
        // calculate comparator for a new cell
        var idx = collection.indexOf(this);
        if (idx == collection.length - 1) { 
            var position = this.get('position') + App.PositionGap;
        } else { 
            var next = collection.at(idx + 1);
            var position = Math.round( (this.get('position') + next.get('position')) /2 );
        }
        this.collection.add({'position': position, 'mode': this.get('mode')});
    },
});

App.Models.Notebook = Backbone.Model.extend({

    url: function() {
        return '/notebooks/' + this.id 
    },
    
    evalUrl: function() {
        return '/engine/' + this.id 
    },

    toggleMode: function(cell) { 
        // console.log(cell.get('mode') ) ;
        if (cell.get('mode')  == 'code') { cell.set({mode: 'text'}) }
        else { cell.set({mode: 'code'}) }
    },
    
    engineEvaluate: function(input, handler) {
        console.log('engineEvaluate');
        var data = JSON.stringify(
            {method:'evaluate', 'input':input}
        );

        $.ajax({
                url: this.evalUrl(),
                type:'POST',
                data:data,
                dataType:'json',
                success: handler
        });
        return;
    },
    
    engineStart: function() {
        $.ajax({
            url: this.evalUrl(),
            type:'POST',
            data: JSON.stringify({method:'start', params: [], id: 1}),
            dataType:'json',
            success: function() { console.log('started engine') }
        });
    }
    
});


App.Collections.Cells = Backbone.Collection.extend({
    
    model: App.Models.Cell,
    
    comparator : function(cell) {
      return cell.get("position");
    },
    
    url: function() {
        return '/notebooks/' + this.notebook.id + '/cells'
    },
    
    initialize: function(options) {
        this.notebook = options.notebook
    },
    
    
});

App.Controllers.Notebooks = Backbone.Controller.extend({
    routes: {
        "":                         "index",
        "notebook/:id":            "edit",
    },
    
    index: function() {
        console.log('index');
        var view = new App.Views.Index();
        // $('#app').html(view.el);
    },
    
    edit: function(id) {
        window.notebook = new App.Models.Notebook({ id: id });
        window.cells = new App.Collections.Cells({ notebook: window.notebook });
        window.view = new App.Views.Edit({ model: window.notebook, collection: window.cells });
        // $('#app').html(window.view.el);
                
        console.log('fetching doc');
        window.notebook.fetch({'error': function() {alert('fetching data failed')}});
        console.log('fetching cells')
        window.cells.fetch({'success': window.view.addAll});
        window.notebook.engineStart();
    },
    
});

App.Views.Edit = Backbone.View.extend({
    
    _cellViews: {},
    
    initialize: function() {
        // console.log('init edit');
        this.el = $('#app');
        _.bindAll(this, 'render', 'close', 'addOne', 'addAll', 'remove');
        this.model.bind('change', this.render);
        this.collection.bind('add', this.addOne);
        this.collection.bind('remove', this.remove);   
        this.scrollToNewCell = true;
    },
    
    render: function() {
        console.log('App.Views.Edit render ' + this.model.get('title')); 
        this.$('#title').html(this.model.get('title'));
        return this;
    },
    
    addOne: function(cell) {
        // console.log('add one cell ' + cell.id + ' ' + cell.cid); 
        var view = new App.Views.Cell({model: cell});
        this._cellViews[cell.cid] = view;
            
        // insert at the correct place
        var newel = view.render().el;
        var visible = this.$('.' + view.className);
        var idx = this.collection.indexOf(cell);
        
        // console.log(visible.length + ' ' + idx);
        if (visible.length == idx) {
            // console.log('append '  + this.el + ' ' + visible.length);
            var notebookEl = this.$('#notebook');
            $(notebookEl).append(newel);
        }
        else {
            // console.log('before ' + idx+ ' ' + visible.length)
            visible.eq(idx).before(newel);           
        }
        // ace can only be initialized once in the DOM
        view.initializeEditor();
        if (this.scrollToNewCell) {checkIfInView(newel);}
        
    },
    
    addAll: function() { 
        this.scrollToNewCell = false
        this.collection.each(this.addOne);
        this.scrollToNewCell = true
    },
    
    remove: function(cell) {
        // console.log('vr ' + cell);
        var view = this._cellViews[cell.cid];
        $(view.el).remove();
    },
    
    focusUp: function(fromCell) { 
        // https://github.com/documentcloud/backbone/issues/136
        var pos = this.collection.indexOf(fromCell);
        if (pos != 0) { 
            var next = this.collection.at(pos - 1);
            this._cellViews[next.cid].getSpawner().focus();
        };
    },
    
    focusDown: function(fromCell) {
         var pos = this.collection.indexOf(fromCell);
         if (pos != this.collection.length - 1) { 
             var next = this.collection.at(pos + 1);
             next = this._cellViews[next.cid];
             next.focusEditor("above");
         };
    },
    
});

App.Views.Cell = Backbone.View.extend({
    
    className: 'cell',
    
    events: {
        "dblclick"                  : "evaluate",
        "evaluate"                  : "evaluate", 
        "inputFocusUp"              : "inputFocusUp",
        "inputFocusDown"            : "inputFocusDown",
        "keydown"                   : "keyDown",
        "togglemode"                : "toggleMode", 
        "delete"                    : "delete",
        // "focus .output"             : "focusIo",
        "focus .input"              : "inputFocused",
        "blur .input"             : "inputBlur",
        // "focus .spawner"            : "focusSpawn",
    },
    

    
    inputChange: function() { 
        // resize the editor if the document length has changed
        // TODO: handle wrapped lines.
        var curLen = this.ace.getSession().doc.getLength();
        if (curLen != this.inputLength) { 
            this.inputLength = curLen;
            var lh = this.ace.renderer.lineHeight; 
            this.$('.ace-container').height(lh * curLen);
            this.ace.resize()
        }
    },
    
    initialize: function() {
        // console.log('cell view');
        _.bindAll(this, 'render', 'close', 'evaluate', 'id', 'keyDown',
            'getSpawner', 'toggleMode', 'inputChange', 'inputFocused', 'inputBlur',
            'initializeEditor', 'evaluateFinish', 'delete'
        );
        this.model.bind('change', this.render);
        // this.bind('cell.evaluate', this.evaluate);
        var cell_template =  _.template($('#cell-template').html());
        var out = cell_template({'model': this.model}) ;    
        // console.log(out);
        window.foo = this.el;
        $(this.el).html(out);
        this.inputLength = 0;
    },
    
    render: function() {
        // console.log('App.Views.Cell.render');
        // var outp = this.getOutput();
        // var newc = this.model.get('output')
        // outp.fadeOut(function() { 
        //     outp.html(newc);
        //     
        //     outp.fadeIn();
        // });
        this.getOutput().html(this.model.get('output'));
        MathJax.Hub.Queue(["Typeset",MathJax.Hub, this.getOutput()[0]]);
        this.getMode().html(this.model.get('mode'));
        this.setEditorHighlightMode();
        
        return this;
    },

    initializeEditor: function() { 
        // we cannot create an editor until its in the DOM
        // so this gets called by the page view after initial render
        // console.log('vi ' + view.$('.input')[0].id + ' ' + this.model.get('input'));
        this.ace = ace.edit(this.$('.input')[0].id);
        this.ace.getSession().setUseWrapMode(true);
        this.ace.renderer.setShowGutter(false);
        this.ace.renderer.setHScrollBarAlwaysVisible(false);
        this.ace.renderer.setShowPrintMargin(false);
        this.ace.setHighlightActiveLine(false);
        
        // hide scrollbar
        this.$('.ace_sb').css({overflow: 'hidden'});
        
        this.ace.getSession().on('change', this.inputChange);
        // trigger initial sizing of element.  TODO: correctly size when creating template
        this.inputChange();
        
        this.setEditorHighlightMode();
    },
    
    setEditorHighlightMode: function() { 
        if (!this.ace) { return }
        if (this.model.get('mode') == 'code') { 
            var Mode = require("ace/mode/python").Mode;
        }
        else if (this.model.get('mode') == 'text') { 
            var Mode = require("ace/mode/text").Mode;
        }
        console.log(this.ace + ' ' + Mode + ' ' + this.model.mode);
        this.ace.getSession().setMode(new Mode());
    },
    
    delete: function() { 
        window.view.focusUp(this.model); 
        this.model.destroy();
        window.cells.remove(this.model);
    },
    
    evaluate: function() { 
        // console.log('eval cell' + this.ace.getSession().getValue());
        // this.getOutput().fadeOut();
        this.getOutput().addClass('evaluating');
        this.model.evaluate(this.ace.getSession().getValue(), this.evaluateFinish);
    },
    
    evaluateFinish: function() { 
        console.log(this);
        this.getOutput().removeClass('evaluating');
        this.getOutput().hide();
        this.getOutput().fadeIn();
    },
    
    getInput: function() {      return this.ace                     },
    getOutput: function() {     return this.$('.output').first()    },
    getSpawner: function() {    return this.$('.spawner').first()   },
    getMode: function() {       return this.$('.mode').first()   },
    
    // key up through cell
    inputFocusUp: function() {      window.view.focusUp(this.model);    },
    outputFocusUp: function() {     this.focusEditor("below")           },
    spawnFocusUp: function() {      this.getOutput().focus()            },
    
    // key down through cell
    inputFocusDown: function() {    this.getOutput().focus();           },
    outputFocusDown: function() {   this.getSpawner().focus()           },
    spawnFocusDown: function() {    window.view.focusDown(this.model)   },
    
    // ace shows line highlight only when focused
    inputFocused: function() { if (this.ace) {this.ace.setHighlightActiveLine(true)} },
    inputBlur: function() { this.ace.setHighlightActiveLine(false); },
    
    focusEditor: function(from) {
        // TODO: dont destroy cursor horizontal position
        this.ace.focus();         
        if (from=="above") { this.ace.navigateFileStart() };
        if (from=="below") { this.ace.navigateFileEnd()}
        checkIfInView(this.$('.input'))
        // this.ace.setHighlightActiveLine(true);
    },
    
    toggleMode: function() { 
        window.notebook.toggleMode(this.model); 
    },
    
    keyDown: function(ev) { 
        // could place the keydown code here instead of ace-events.js
        // but I need a better dispatch than this crap...
        console.log('kd ' + ev.keyCode + ' ' +  ev.target.id + ' ' + $(ev.target).hasClass('output'))

        if (ev.keyCode == 38 && $(ev.target).hasClass('output')) { this.outputFocusUp(); };
        if (ev.keyCode == 40 && $(ev.target).hasClass('output')) { this.outputFocusDown(); };
        if (ev.keyCode == 38 && $(ev.target).hasClass('spawner')) { this.spawnFocusUp(); };
        if (ev.keyCode == 40 && $(ev.target).hasClass('spawner')) { this.spawnFocusDown(); };
        
        // TODO: stop this text propagating to new cell somehow?
        if (ev.keyCode == 13 && $(ev.target).hasClass('spawner')) { this.model.addAfter(window.cells); return false; };
        if (ev.keycode == 8) { return false }
    },
    
});



App.Views.Index = Backbone.View.extend({
    initialize: function() {
        console.log('init');
        this.render();
    },
    
    render: function() {
        console.log('App.Views.Index render');
        out = "<h3>No documents! <a href='#new'>Create one</a></h3><a href=\"#notebook/1\">foo</a>";        
        $(this.el).html(out);
        return this;
    }
});


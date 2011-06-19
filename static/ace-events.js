// rebind events in the ace editor
var canon = require('pilot/canon');

canon.addCommand({
    name: 'evaluate',
    bindKey: { win: 'Ctrl-E', mac: 'Command-E', sender: 'editor' },
    exec: function(env, args, request) {
        $(env.editor.container).trigger('evaluate');
    }
})

canon.addCommand({
    name: 'togglemode',
    bindKey: { win: 'Ctrl-M', mac: 'Command-M', sender: 'editor' },
    exec: function(env, args, request) {
        $(env.editor.container).trigger('togglemode');
    }
})

canon.addCommand({
    name: 'golineup',
    bindKey: {win: 'Up', mac: 'Up', sender: 'editor'},
    exec: function(env, args, request) {
        var row = env.editor.getCursorPosition().row;
        env.editor.navigateUp(args.times);
        if (row == 0) { $(env.editor.container).trigger('inputFocusUp'); }
    }
});

canon.addCommand({
    name: 'golinedown',
    bindKey: {win: 'Down', mac: 'Down', sender: 'editor'},
    exec: function(env, args, request) {
        var row = env.editor.getCursorPosition().row;
        var lastRow = env.editor.getSession().doc.getLength() - 1;
        // console.log('down called on row ' + row);
        env.editor.navigateDown(args.times);
        if (row == lastRow) { $(env.editor.container).trigger('inputFocusDown'); }
    }
});

canon.addCommand({
    name: "backspace",
    bindKey: {
        win: "Ctrl-Backspace|Command-Backspace|Option-Backspace|Shift-Backspace|Backspace",
        mac: "Ctrl-Backspace|Command-Backspace|Shift-Backspace|Backspace|Ctrl-H",
        sender: 'editor'
    },
    exec: function(env, args, request) { 
        console.log('backspace');
        window.env = [env, args, request];
        if (env.editor.getSession().getValue() == "") {   env.editor.removeLeft(); $(env.editor.container).trigger('delete');}
        else { env.editor.removeLeft() }
    }
});

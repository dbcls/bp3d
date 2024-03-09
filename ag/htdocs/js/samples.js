/*
 * Ext JS Library 2.2
 * Copyright(c) 2006-2008, Ext JS, LLC.
 * licensing@extjs.com
 * 
 * http://extjs.com/license
 */

SamplePanel = Ext.extend(Ext.DataView, {
    autoHeight: true,
    frame:true,
    cls:'demos',
    itemSelector: 'dd',
    overClass: 'over',
    
    tpl : new Ext.XTemplate(
        '<div id="sample-ct">',
            '<tpl for=".">',
            '<div><h2><div>{title}</div></h2>',
            '<dl>',
                '<tpl for="species">',
                    '<dd ext:txpath="/root/{txpath}"><img src="icon/{icon}"/>',
                        '<div><h4>{name}</h4><p>{detail}</p></div>',
                    '</dd>',
                '</tpl>',
            '<div style="clear:left"></div></dl></div>',
            '</tpl>',
        '</div>'
    ),

    onClick : function(e){
        var group = e.getTarget('h2', 3, true);
        if(group){
            group.up('div').toggleClass('collapsed');
        }else {
            var t = e.getTarget('dd', 5, true);
            if(t && !e.getTarget('a', 2)){
                var txpath = t.getAttributeNS('ext', 'txpath');
//                alert(txpath);
								var treeCmp = Ext.getCmp('tree-panel');
								if(treeCmp) treeCmp.selectPath(txpath,undefined,selectPathCB);
            }
        }
        return SamplePanel.superclass.onClick.apply(this, arguments);
    }
});

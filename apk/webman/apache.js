/* Copyright (c) 2026 Cappysan. All rights reserved. */

Ext.define('AS.ARC.apps.cappysanapache.core', {
    extend: 'Ext.util.Observable',

    apiUrl: AS.ARC.util.getUserAppsPath() + 'cappysan-apache/' + 'apache.cgi',

    constructor: function (config) {
        Ext.apply(this, config);
        this.callParent();
        this.init(config);
    },

    init: function () {
        var fn = this;

        fn.win = fn.desktop.createWindow({
            app:       fn.app,
            id:        fn.id,
            itemId:    fn.id,
            title:     '<div class="as-header" style="background-image:url(' + AS.ARC.util.fixDc('/apps/cappysan-apache/images/icon-app-task.png') + ');background-position:50%;background-repeat:no-repeat;"></div><div class="as-header-text">Apache</div>',
            width:     700,
            height:    500,
            minWidth:  700,
            minHeight: 500,
            resizable: true,
            border:    false,
            layout:    'fit',
            items:     [fn.getMainPanel()],
            listeners: {
                afterrender: function (win) {
                    win.header.items.items[1].hide();
                    fn.navGrid.getSelectionModel().select(0);
                }
            }
        });
    },

    getNavGrid: function () {
        var fn = this;

        fn.navGrid = Ext.create('Ext.grid.Panel', {
            itemId: 'navGrid',
            store: Ext.create('Ext.data.ArrayStore', {
                fields: ['title', 'tabId'],
                data: [
                    [_S('APACHE', 'TAB_SETTINGS'), 'settings'],
                    [_S('APACHE', 'TAB_SITES'),    'sites'],
                    [_S('APACHE', 'TAB_DEFAULT'),  'apache']
                ]
            }),
            hideHeaders: true,
            height:      '100%',
            border:      false,
            columns: [{
                flex:     1,
                renderer: function (v, metadata, record) {
                    var icons = {
                        settings: AS.ARC.util.fixDc('/apps/cappysan-apache/images/icon-fn-settings.png'),
                        sites:    AS.ARC.util.fixDc('/apps/cappysan-apache/images/icon-fn-apache.png'),
                        apache:   AS.ARC.util.fixDc('/apps/cappysan-apache/images/icon-fn-sites.png')
                    };
                    var iconUrl = icons[record.data.tabId] || icons.settings;
                    return '<div class="fn-block">' +
                           '<div class="fn-icon" style="background-image:url(' + iconUrl + ');background-repeat:no-repeat;background-position:center center;background-size:contain;"></div>' +
                           '<div class="fn-title" style="width:130px;opacity:1;">' + record.data.title + '</div>' +
                           '<div class="x-clear"></div>' +
                           '</div>';
                }
            }],
            listeners: {
                selectionchange: function (model, selections) {
                    if (selections.length > 0) {
                        fn.switchTab(selections[0].get('tabId'));
                    }
                }
            }
        });

        return fn.navGrid;
    },

    switchTab: function (tabId) {
        var fn        = this,
            cardPanel = fn.win.down('#cardPanel');

        fn.win.el.mask(_S('COMMON', 'LOADING'));

        AS.ARC.ajax({
            url:    AS.ARC.util.getApiUrlWithSid(fn.apiUrl, { act: 'get', tab: tabId }),
            method: 'post',
            success: function (json) {
                fn.win.el.unmask();
                cardPanel.removeAll();
                if (tabId === 'settings') { fn.renderSettingsTab(cardPanel, json); }
                if (tabId === 'sites')    { fn.renderSitesTab(cardPanel, json); }
                if (tabId === 'apache')   { fn.renderApacheTab(cardPanel, json); }
            },
            failure: function (json) {
                fn.win.el.unmask();
                AS.ARC.util.showMsgWindow({ 5000: _S('COMMON', 'SESSION_TIMEOUT') }, json, fn.win);
            }
        });
    },

    /* ── Settings tab ───────────────────────────────────────────────────── */
    renderSettingsTab: function (cardPanel, json) {
        var fn         = this,
            labelWidth = 150;

        cardPanel.add(Ext.create('Ext.panel.Panel', {
            cls:        'as-page-panel app-cappysan-apache',
            border:     false,
            layout:     'anchor',
            autoScroll: true,
            defaults:   { anchor: '100%' },
            items: [{
                xtype:    'fieldset',
                title:    _S('APACHE', 'SECTION_LINK'),
                defaults: { anchor: '100%' },
                items: [{
                    xtype:  'fieldcontainer',
                    layout: 'hbox',
                    items: [{
                        xtype:  'displayfield',
                        itemId: 'apacheLink',
                        value:  (function () {
                            var url = json.web_url_override || ('https://' + (json.server_name || 'nas.example.com') + '/');
                            return '<a href="' + url + '" target="_blank">' + _S('APACHE', 'LINK_OPEN') + '</a>';
                        })(),
                        margin: '0 10 0 0'
                    }, {
                        xtype:     'textfield',
                        itemId:    'apacheLinkOverride',
                        emptyText: _S('APACHE', 'LINK_OVERRIDE_HINT'),
                        flex:      1,
                        value:     json.web_url_override || '',
                        listeners: {
                            change: function (field, newVal) {
                                var linkField = fn.win.down('#apacheLink');
                                if (linkField) {
                                    var url = newVal || ('https://' + (json.server_name || 'nas.example.com') + '/');
                                    linkField.setValue('<a href="' + url + '" target="_blank">' + _S('APACHE', 'LINK_OPEN') + '</a>');
                                }
                            }
                        }
                    }]
                }]
            }, {
                xtype:    'fieldset',
                title:    _S('APACHE', 'SECTION_SERVER'),
                defaults: { anchor: '100%', msgTarget: AS.ARC.config.msgTarget },
                items: [{
                    xtype:      'textfield',
                    fieldLabel: AS.ARC.util.fontToBold(_S('APACHE', 'LABEL_SERVER_NAME')),
                    labelWidth: labelWidth,
                    itemId:     'settingsServerName',
                    emptyText:  'nas.example.com',
                    value:      json.server_name || ''
                }, {
                    xtype:      'textfield',
                    fieldLabel: AS.ARC.util.fontToBold(_S('APACHE', 'LABEL_DOMAIN')),
                    labelWidth: labelWidth,
                    itemId:     'settingsDomain',
                    emptyText:  'example.com',
                    value:      json.domain || ''
                }, {
                    xtype:      'textfield',
                    fieldLabel: AS.ARC.util.fontToBold(_S('APACHE', 'LABEL_ADMIN_EMAIL')),
                    labelWidth: labelWidth,
                    itemId:     'settingsAdminEmail',
                    emptyText:  'admin@example.com',
                    value:      json.admin_email || ''
                }]
            }],
            dockedItems: [{
                xtype: 'toolbar',
                dock:  'bottom',
                ui:    'footer',
                items: [
                    { xtype: 'component', flex: 1 },
                    {
                        xtype:   'button',
                        text:    _S('APACHE', 'BTN_RESTART'),
                        handler: function () { fn.restartApache(); }
                    },
                    {
                        xtype:   'button',
                        text:    _S('APACHE', 'BTN_RELOAD'),
                        handler: function () { fn.reloadApache(); }
                    },
                    {
                        xtype:   'button',
                        text:    _S('COMMON', 'APPLY'),
                        handler: function () { fn.saveSettingsTab(); }
                    }
                ]
            }]
        }));
    },

    saveSettingsTab: function () {
        var fn          = this,
            serverName  = fn.win.down('#settingsServerName'),
            domain      = fn.win.down('#settingsDomain'),
            adminEmail  = fn.win.down('#settingsAdminEmail'),
            urlOverride = fn.win.down('#apacheLinkOverride');

        fn.win.el.mask(_S('COMMON', 'APPLYING'));
        AS.ARC.ajax({
            url:    AS.ARC.util.getApiUrlWithSid(fn.apiUrl, { act: 'set', tab: 'settings' }),
            method: 'post',
            params: {
                server_name:       serverName  ? serverName.getValue()  : '',
                domain:            domain      ? domain.getValue()      : '',
                admin_email:       adminEmail  ? adminEmail.getValue()  : '',
                web_url_override:  urlOverride ? urlOverride.getValue() : ''
            },
            success: function () {
                fn.win.el.unmask();
                fn.switchTab('settings');
            },
            failure: function (json) {
                fn.win.el.unmask();
                AS.ARC.util.showMsgWindow({ 5000: _S('COMMON', 'SESSION_TIMEOUT') }, json, fn.win);
            }
        });
    },

    /* ── Sites tab ──────────────────────────────────────────────────────── */
    renderSitesTab: function (cardPanel, json) {
        var fn    = this,
            sites = json.sites || [];

        var store = Ext.create('Ext.data.Store', {
            pageSize: 5,
            fields: ['name', 'enabled'],
            data:   sites
        });

        var grid = Ext.create('Ext.grid.Panel', {
            itemId:          'sitesGrid',
            store:           store,
            border:          false,
            sortableColumns: false,
            anchor:          '100%',
            height:          200,
            style: { border: '#BBB 1px solid' },
            columns: [{
                header:       _S('APACHE', 'COL_SITE_NAME'),
                dataIndex:    'name',
                menuDisabled: true,
                flex:         2
            }, {
                header:       _S('APACHE', 'COL_SITE_STATUS'),
                dataIndex:    'enabled',
                menuDisabled: true,
                flex:         1,
                renderer:  function (v) {
                    return v
                        ? '<span style="color:#2a7a2a;">' + _S('APACHE', 'STATUS_ENABLED')  + '</span>'
                        : '<span style="color:#a32d2d;">' + _S('APACHE', 'STATUS_DISABLED') + '</span>';
                }
            }],
            listeners: {
                selectionchange: function (model, sel) {
                    var has       = sel.length > 0;
                    var enabled   = has && sel[0].get('enabled');
                    var isDefault = has && sel[0].get('name') === '_default_.conf';
                    fn.win.down('#enableBtn').setDisabled(!has || enabled);
                    fn.win.down('#disableBtn').setDisabled(!has || !enabled || isDefault);
                    if (has) { fn.loadSiteContent(sel[0].get('name')); }
                }
            },
            bbar: Ext.create('AS.ARC.pagingToolbar', { store: store })
        });

        cardPanel.add(Ext.create('Ext.panel.Panel', {
            cls:    'as-page-panel app-cappysan-apache',
            border: false,
            layout: {
                type:  'vbox',
                align: 'stretch'
            },
            items: [{
                xtype:    'fieldset',
                title:    _S('APACHE', 'SECTION_SITES'),
                defaults: { anchor: '100%' },
                flex:     0,
                items: [{
                    xtype:  'box',
                    autoEl: { tag: 'div' },
                    style:  'margin-bottom: 8px;',
                    html:   'Notice: /etc/hosts entries can be configured with the cappysan-persistence package.'
                }, {
                    xtype: 'toolbar',
                    items: [{
                        text:     _S('APACHE', 'BTN_ENABLE'),
                        itemId:   'enableBtn',
                        disabled: true,
                        handler:  function () { fn.toggleSite(true); }
                    }, {
                        text:     _S('APACHE', 'BTN_DISABLE'),
                        itemId:   'disableBtn',
                        disabled: true,
                        handler:  function () { fn.toggleSite(false); }
                    }]
                }, grid]
            }, {
                xtype:  'fieldset',
                title:  _S('APACHE', 'SECTION_SITE_CONTENT'),
                flex:   1,
                layout: 'fit',
                items: [{
                    xtype:    'textarea',
                    itemId:   'siteContent',
                    readOnly: true,
                    cls:      'apache-conf-view',
                    value:    ''
                }]
            }],
            dockedItems: [{
                xtype: 'toolbar',
                dock:  'bottom',
                ui:    'footer',
                items: [
                    { xtype: 'component', flex: 1 },
                    {
                        xtype:   'button',
                        text:    _S('APACHE', 'BTN_RESTART'),
                        handler: function () { fn.restartApache(); }
                    },
                    {
                        xtype:   'button',
                        text:    _S('APACHE', 'BTN_RELOAD'),
                        handler: function () { fn.reloadApache(); }
                    },
                    {
                        xtype:   'button',
                        text:    _S('COMMON', 'APPLY'),
                        handler: function () { fn.reloadApache(); }
                    }
                ]
            }]
        }));
    },

    reloadApache: function () {
        var fn = this;
        fn.win.el.mask(_S('COMMON', 'APPLYING'));
        AS.ARC.ajax({
            url:    AS.ARC.util.getApiUrlWithSid(fn.apiUrl, { act: 'reload' }),
            method: 'post',
            success: function (json) {
                fn.win.el.unmask();
                if (json && json.warning) {
                    AS.ARC.msgWindow.show({ parentWin: fn.win, title: _S('COMMON', 'WARNING'), width: 400, height: 160, iconType: 'warn', asItems: [{ xtype: 'displayfield', value: json.warning }], fbar: [{ text: _S('COMMON', 'OK'), handler: function () { this.up('window').close(); } }] });
                }
            },
            failure: function (json) {
                fn.win.el.unmask();
                AS.ARC.util.showMsgWindow({ 5000: _S('COMMON', 'SESSION_TIMEOUT') }, json, fn.win);
            }
        });
    },

    restartApache: function () {
        var fn = this;
        fn.win.el.mask(_S('COMMON', 'APPLYING'));
        AS.ARC.ajax({
            url:    AS.ARC.util.getApiUrlWithSid(fn.apiUrl, { act: 'restart' }),
            method: 'post',
            success: function (json) {
                fn.win.el.unmask();
                if (json && json.warning) {
                    AS.ARC.msgWindow.show({ parentWin: fn.win, title: _S('COMMON', 'WARNING'), width: 400, height: 160, iconType: 'warn', asItems: [{ xtype: 'displayfield', value: json.warning }], fbar: [{ text: _S('COMMON', 'OK'), handler: function () { this.up('window').close(); } }] });
                }
            },
            failure: function (json) {
                fn.win.el.unmask();
                AS.ARC.util.showMsgWindow({ 5000: _S('COMMON', 'SESSION_TIMEOUT') }, json, fn.win);
            }
        });
    },

    loadSiteContent: function (name) {
        var fn = this;
        AS.ARC.ajax({
            url:    AS.ARC.util.getApiUrlWithSid(fn.apiUrl, { act: 'get_content', name: name }),
            method: 'post',
            success: function (json) {
                var area = fn.win.down('#siteContent');
                if (area) { area.setValue(json.content || ''); }
            },
            failure: function () {}
        });
    },

    toggleSite: function (enable) {
        var fn  = this,
            grid = fn.win.down('#sitesGrid'),
            sel  = grid.getSelectionModel().getSelection();
        if (!sel.length) { return; }
        var name = sel[0].get('name');

        fn.win.el.mask(_S('COMMON', 'APPLYING'));
        AS.ARC.ajax({
            url:    AS.ARC.util.getApiUrlWithSid(fn.apiUrl, { act: 'set', tab: 'sites' }),
            method: 'post',
            params: { name: name, enabled: enable ? 'true' : 'false' },
            success: function (json) {
                fn.win.el.unmask();
                if (json && json.warning) {
                    AS.ARC.msgWindow.show({ parentWin: fn.win, title: _S('COMMON', 'WARNING'), width: 400, height: 160, iconType: 'warn',
                        asItems: [{ xtype: 'displayfield', value: json.warning }],
                        fbar: [{ text: _S('COMMON', 'OK'), handler: function () { this.up('window').close(); } }]
                    });
                }
                fn.switchTab('sites');
            },
            failure: function (json) {
                fn.win.el.unmask();
                AS.ARC.util.showMsgWindow({ 5000: _S('COMMON', 'SESSION_TIMEOUT') }, json, fn.win);
            }
        });
    },

        /* ── Persistence link ──────────────────────────────────────────────────── */
    openPersistenceHosts: function () {
        var fn      = this,
            launched = false;

        // Walk all registered ExtJS components looking for persistence app
        try {
            Ext.ComponentManager.each(function (id, cmp) {
                if (cmp && cmp.appTag === 'cappysan-persistence' && cmp.createWindow) {
                    cmp.createWindow();
                    launched = true;
                    return false;
                }
            });
        } catch (e) {}

        // Try taskbar items
        if (!launched) {
            try {
                var tb = fn.app.core.getDesktop().taskBar;
                if (tb && tb.items) {
                    tb.items.each(function (item) {
                        if (item.app && item.app.appTag === 'cappysan-persistence') {
                            item.app.createWindow();
                            launched = true;
                            return false;
                        }
                    });
                }
            } catch (e) {}
        }

        if (!launched) {
            Ext.Msg.alert(
                'cappysan-persistence',
                'Please open cappysan-persistence from the desktop and go to the Hosts tab.'
            );
        }
    },

    /* ── Persistence launcher ──────────────────────────────────────────── */
    launchPersistence: function () {
        // Try every known way to launch a third-party ADM app
        var fn = this;

        // 1. AS.ARC.core.openApp (works for built-in app-* apps; try the package name)
        try {
            if (AS.ARC.core && AS.ARC.core.openApp) {
                AS.ARC.core.openApp('cappysan-persistence', 'hosts');
                return;
            }
        } catch (e) {}

        // 2. Direct module instantiation: each ADM app exposes AS.ARC.apps.<name>.main
        try {
            if (Ext.ClassManager.isCreated('AS.ARC.apps.persistence.main')) {
                var app = Ext.create('AS.ARC.apps.persistence.main', { core: fn.app.core });
                if (app && app.createWindow) {
                    app.createWindow();
                    return;
                }
            }
        } catch (e) {}

        // 3. Walk the desktop taskbar
        try {
            var tb = fn.app.core.getDesktop().taskBar;
            if (tb && tb.items) {
                var found = false;
                tb.items.each(function (item) {
                    if (item.app && item.app.appTag === 'cappysan-persistence') {
                        item.app.createWindow();
                        found = true;
                        return false;
                    }
                });
                if (found) { return; }
            }
        } catch (e) {}

        Ext.Msg.alert('cappysan-persistence',
            'Could not open cappysan-persistence. Please open it from the desktop and go to the Hosts tab.');
    },

    /* ── Apache (self-registration) tab ───────────────────────────────── */
    renderApacheTab: function (cardPanel, json) {
        var fn = this;

        cardPanel.add(Ext.create('Ext.panel.Panel', {
            cls:        'as-page-panel app-cappysan-apache',
            border:     false,
            layout:     'anchor',
            autoScroll: true,
            defaults:   { anchor: '100%' },
            items: [{
                xtype:    'fieldset',
                title:    _S('APACHE', 'SECTION_APACHE_SETTINGS'),
                defaults: { anchor: '100%', msgTarget: AS.ARC.config.msgTarget },
                items: [{
                    xtype:      'textfield',
                    fieldLabel: _S('APACHE', 'LABEL_APACHE_HOSTNAME'),
                    itemId:     'apacheHostname',
                    emptyText:  'nas',
                    value:      json.apache_hostname || ''
                }, {
                    xtype:      'textfield',
                    fieldLabel: _S('APACHE', 'LABEL_APACHE_FQDN'),
                    itemId:     'apacheFqdn',
                    emptyText:  '${hostname}.${domain}',
                    value:      json.apache_fqdn || ''
                }, {
                    xtype: 'displayfield',
                    value: _S('APACHE', 'LABEL_APACHE_PLACEHOLDERS')
                }, {
                    xtype:      'textfield',
                    fieldLabel: _S('APACHE', 'LABEL_APACHE_REDIRECT'),
                    itemId:     'apacheRedirect',
                    emptyText:  'https://${server_fqdn}/',
                    value:      json.apache_redirect_to || ''
                }, {
                    xtype:      'textfield',
                    fieldLabel: _S('APACHE', 'LABEL_APACHE_PROXY_TO'),
                    itemId:     'apacheProxyTo',
                    emptyText:  'https://127.0.0.1:8001/',
                    value:      json.apache_proxy_to || ''
                }]
            }],
            dockedItems: [{
                xtype: 'toolbar',
                dock:  'bottom',
                ui:    'footer',
                items: [
                    { xtype: 'component', flex: 1 },
                    {
                        xtype:   'button',
                        text:    _S('APACHE', 'BTN_RESTART'),
                        handler: function () { fn.restartApache(); }
                    },
                    {
                        xtype:   'button',
                        text:    _S('APACHE', 'BTN_RELOAD'),
                        handler: function () { fn.reloadApache(); }
                    },
                    {
                        xtype:   'button',
                        text:    _S('COMMON', 'APPLY'),
                        handler: function () { fn.saveApacheTab(); }
                    }
                ]
            }]
        }));
    },

    saveApacheTab: function () {
        var fn       = this,
            hostname = fn.win.down('#apacheHostname'),
            fqdn     = fn.win.down('#apacheFqdn'),
            redirect = fn.win.down('#apacheRedirect'),
            proxyTo  = fn.win.down('#apacheProxyTo');

        fn.win.el.mask(_S('COMMON', 'APPLYING'));
        AS.ARC.ajax({
            url:    AS.ARC.util.getApiUrlWithSid(fn.apiUrl, { act: 'set', tab: 'apache' }),
            method: 'post',
            params: {
                apache_hostname:    hostname ? hostname.getValue() : 'nas',
                apache_fqdn:        fqdn     ? fqdn.getValue()     : '${hostname}.${domain}',
                apache_redirect_to: redirect ? redirect.getValue() : 'https://${server_fqdn}/',
                apache_proxy_to:    proxyTo  ? proxyTo.getValue()  : 'https://127.0.0.1:8001/'
            },
            success: function (json) {
                fn.win.el.unmask();
                if (json && json.warning) {
                    AS.ARC.msgWindow.show({ parentWin: fn.win, title: _S('COMMON', 'WARNING'), width: 400, height: 160, iconType: 'warn', asItems: [{ xtype: 'displayfield', value: json.warning }], fbar: [{ text: _S('COMMON', 'OK'), handler: function () { this.up('window').close(); } }] });
                }
                fn.switchTab('apache');
            },
            failure: function (json) {
                fn.win.el.unmask();
                AS.ARC.util.showMsgWindow({ 5000: _S('COMMON', 'SESSION_TIMEOUT') }, json, fn.win);
            }
        });
    },

    /* ── Layout ─────────────────────────────────────────────────────────── */
    getMainPanel: function () {
        var fn = this;

        return Ext.create('Ext.panel.Panel', {
            itemId: 'main',
            border: false,
            layout: 'border',
            items: [{
                region: 'west',
                itemId: 'westPanel',
                cls:    'as-selector-panel',
                border: false,
                width:  150,
                layout: 'fit',
                items:  [fn.getNavGrid()]
            }, {
                region: 'center',
                xtype:  'panel',
                itemId: 'cardPanel',
                border: false,
                layout: 'fit'
            }]
        });
    }
});

Ext.define('AS.ARC.apps.cappysanapache.main', {
    extend:     'AS.ARC._appBase',
    appTag:     'cappysan-apache',
    title:      'Apache',
    appMaxNum:  1,
    appOpenNum: 0,
    appIsReady: true,
    appWins:    [],

    createWindow: function () {
        var desktop = this.core.getDesktop(),
            app     = this;

        if ((this.appOpenNum === this.appMaxNum) || !this.appIsReady) {
            this.appWins[0].show();
            return;
        }

        this.appIsReady = false;

        var apache = Ext.create('AS.ARC.apps.cappysanapache.core', {
            app:     this,
            desktop: desktop,
            id:      this.id + '-' + Ext.id()
        });

        apache.win.on('render', function () {
            app.appOpenNum++;
            app.appIsReady = true;
        });

        apache.win.on('beforeclose', function () {
            app.appOpenNum--;
            app.appIsReady = true;
            app.appWins.pop();
        });

        apache.win.show();
        this.appWins.push(apache.win);
        return apache.win;
    }
});

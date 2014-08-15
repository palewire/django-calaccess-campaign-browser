'use strict';

var App = App || {};

App = {
    init: function () {
        // App.dataTables();
    },
    dataTables: function () {
        $('table').dataTable();
    }
};

jQuery(document).ready(function($) {
    App.init();
});
var G = function(a, b, c){

    // 拼接字符串
    function d(a, b) {
        return ['著作权归作者所有。',
            '商业转载请联系作者获得授权，非商业转载请注明出处。',
            '作者：' + b,
            '链接：' + a,
            '来源：孙强的个人博客',
            '',
            ''
        ]
    }

    // 拼接成html
    function f(b, c, m) {
        return '<div>' + d(b, c).join('<br />') + m +'</div>'
    }

    // 处理 copy
    function g(a){
        if(!window.getSelection){
            return;
        }


        var m = window.getSelection().toString();

        if ('object' === typeof a.originalEvent.clipboardData) {
            var m = window.getSelection().toString();
            a.originalEvent.clipboardData.setData('text/html', f( b, c));
            a.originalEvent.clipboardData.setData('text/plain', d(b, c).join('\n') + m);
            a.preventDefault();

            return;
        }

        var n = $(f(b, c, m)).css({
            position: 'fixed',
            left: '-9999px'
        }).appendTo('body');
        window.getSelection().selectAllChildren(n[0]);

    }

    function hander(a){
        g(a);
        //alert('复制好了, 请粘贴内容!');
    }

    // 绑定copy事件
	a.on('copy', hander);

}

var a = $('.p1');

G(a, location.href, a.data('name'))


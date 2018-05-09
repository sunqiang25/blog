        (function () {
            var $wrap = $("#wrap"),
                $picLi = $(".pic ul li"),
                $tabLi = $(".tab ul li"),
                $btn = $(".btn div"),
				//jQuery li对象中元素的数目
                length = $picLi.length,
                index = 0,
                timer = null;

            //初始化显示
			//先显示第一pic下第一个li里面的图片
            $picLi.hide().eq(0).show();
			//点击按键改变颜色 默认页面加载点击第一个按钮
            $tabLi.eq(0).addClass("on");

            //tab区域
            $tabLi.click(function () {
               var x = $(this).index();
               if(x !== index){
                   change(x);
               }
            });

            //btn点击  0 1
            $btn.click(function () {
                var x = index;
                if($(this).index()){
                    x ++ ;
                    x %= length;
                }else{
                    x --;
                    if(x<0)x = length - 1;
                }
                change(x);
            });

            //变化函数
            function change(i) {
			/*	使用淡入效果来显示一个隐藏的 <p> 元素：
				$(".btn2").click(function(){
				$("p").fadeIn();
				});
			*/
                $picLi.eq(index).fadeOut();
                $tabLi.eq(index).removeClass("on");
                index = i;
                $picLi.eq(index).fadeIn();
                $tabLi.eq(index).addClass("on");
            }

            //定时器函数
           //auto();
            $wrap.hover(function () {
                clearInterval(timer);
            },auto());

//每隔一秒调用一次change函数，图片切换一次
	/*setInterval() 方法可按照指定的周期
		（以毫秒计）来调用函数或计算表达式。*/
            function auto() {
                timer = setInterval(function () {
                    var x = index;
                    x ++;
                    x %= length;
                    change(x);
                },2000);
//                return auto;//默认返回
            }
        })();
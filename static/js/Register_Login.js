
$(function() {
     //check Login
    $.ajax({
    type:"GET",
    url:"/check_is_login",
    cache:false,
    dataType:'text',
    success:function(result){

        $("#user_part1").html(result);
        //$("#imgId").attr('src',path); 
    },
    error:function(XMLHttpRequest, textStatus, errorThrown){
        //alert(textStatus);
        $("#user_part1").html('<ul class="nav navbar-nav navbar-right"><li style="font-size:20px;"><a href="#" data-toggle="modal" data-target="#LoginModal" >登 录</a></li> <li style="font-size:20px;"><a href="#" data-toggle="modal" data-target="#RegModal" >注 册</a></li></ul>');
    }
});

//登录
$('#login_form').submit(function(){
    //验证
    var tip=$('#login_tip');
    tip.text('');

    if($('#login_name').val()==''){
        tip.text('请输入昵称');
        return false;
    };
    if($('#login_pwd').val()==''){
        tip.text('请输入密码');
        return false;

    };

    //登录
    /*$('#login_csrf').val($.cookie('csrftoken'));*/

    $.ajax({
        type: "POST",
        data: $('#login_form').serialize(),
        url: "/user_login",
        cache: false,
        dataType: "json",
        success: function(json, textStatus){
            var is_success = json['success'];
            if(is_success){
                tip.text('登录成功，页面处理中...');
                window.location.reload();
            }else{
                console.log(json['message'])
                tip.text('用户名或者密码错误，请重试');
            };
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            tip.text("登录出错，请重试 "+errorThrown);
        }
    });
    return false;
});
//注册
$('#reg_form').submit(function(){
    //验证
    var tip=$('#reg_tip');
    tip.text('');

    var reg_uname=$('#reg_uname').val();
    var reg_email=$('#reg_email').val();
    var reg_pwd=$('#reg_pwd').val();

    if(reg_uname==''){
        tip.text('username cannot empty');
        return false;
    }
    if(reg_email==''){
        tip.text('邮箱不能为空');
        return false;
    };
    if(!reg_email.match(/^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/)){
        tip.text('请输入正确的邮箱格式');
        return false;
    }

    if(reg_pwd==''){
        tip.text('密码不能为空');
        return false    ;
    };
    if(reg_pwd.length<6){
        tip.text('密码不能少于6位');
    }

    //注册
    tip.text('注册中，请稍后...');
    /*$('#reg_csrf').val($.cookie('csrftoken'));*/
    $.ajax({
        type: "POST",
        data: $('#reg_form').serialize(),
        url: "/user_reg",
        cache: false,
        dataType: "json",
        success: function(json, textStatus){
            var is_success = json['success'];
            if(is_success){
                tip.text('注册成功，页面处理中...');
                $('#reg_control').text(json['message']);

                window.setTimeout(function(){
                    window.location.reload();
                },3000);
            }else{
                tip.text(json['message']);
            };
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            tip.text("注册出错，请重试 "+errorThrown);
        }
    });
    return false;
});
    });
    function myFunction() {
    var x = document.getElementById("reg_pwd");
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
}

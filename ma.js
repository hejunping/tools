(function () {

    var params = {};
    //Document对象数据
    if(document) {
        params.domain = document.domain || '';
        params.url = document.URL || '';
        params.title = document.title || '';
        params.referrer = document.referrer || '';
    }
    //Window对象数据
    if(window && window.screen) {
        params.sh = window.screen.height || 0;
        params.sw = window.screen.width || 0;
        params.cd = window.screen.colorDepth || 0;
    }
    //navigator对象数据
    if(navigator) {
        params.lang = navigator.language || '';
    }
    //解析_maq配置
    if(_maq) {
        for(var i in _maq) {
            switch(_maq[i][0]) {
                case '_setAccount':
                    params.account = _maq[i][1];
                    break;
                case '_setUserId':
                    params.userid = _maq[i][1];
                    break;
                default:
                    break;
            }
        }
    }
    //拼接参数串
    var args = '';
    for(var i in params) {
        if(args != '') {
            args += '&';
        }
        args += i + '=' + encodeURIComponent(params[i]);
    }

    //通过Image对象请求后端脚本
    var img = new Image(1, 1);
    img.src = 'http://log.xxxx.com/log.gif?' + args;


    var sendData = function(url,referrer){
        var params = {};
        //Document对象数据
        if(document) {
            params.domain = document.domain || '';
            params.url = url || '';
            params.referrer = referrer || '';
        }
        //解析_maq配置
        if(_maq) {
            for(var i in _maq) {
                switch(_maq[i][0]) {
                    case '_setAccount':
                        params.account = _maq[i][1];
                        break;
                    case '_setUserId':
                        params.userid = _maq[i][1];
                        break;
                    default:
                        break;
                }
            }
        }
        //拼接参数串
        var args = '';
        for(var i in params) {
            if(args != '') {
                args += '&';
            }
            args += i + '=' + encodeURIComponent(params[i]);
        }

        //通过Image对象请求后端脚本
        var img = new Image(1, 1);
        img.src = 'http://log.xxxx.com/log.gif?' + args;
    }
    // 监听 职位列表
    if (document.URL.indexOf('hh.xxxx.com/positions.html#/all')>-1) {
        window.addEventListener('load', function(event){
            var addEventListener = function() {
                var smenu = document.getElementsByClassName('postion-title');
                if (smenu.length > 0) {
                    clearInterval(addEventListenerId)
                    for (var i=0;i<smenu.length;i++){
                        smenu[i].addEventListener('click',function(e){
                            var postionclass = this.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.getAttribute("class");
                            var pid = postionclass.replace('position-','');
                            var url = 'https://hh.xxxx.com/position.html#/'+pid
                            var referrer = document.URL;
                            sendData(url, referrer);
                        });
                    }
                };
            };
            var addEventListenerId = setInterval(addEventListener, 1000);
        });
    }

    // h5页面监听
    if (document.URL.indexOf('h5.xxxx.com')>-1) {
        window.addEventListener('load', function(event){
            var addEventListener = function() {
                var smenu = document.getElementsByClassName('position-info');
                var url = document.URL;
                var referrer = ""; 
                if (smenu.length > 0) {
                    clearInterval(addEventListenerId)
                    var bodyClick = document.getElementsByTagName('body')[0];
                    bodyClick.addEventListener('click', function(e){
                        referrer = url;
                        url = document.URL;
                        if (referrer.split("?")[0] != url.split("?")[0]){
                            console.log(url,referrer)
                            sendData(url,referrer);
                        }
                    });
                };
            };
            var addEventListenerId = setInterval(addEventListener, 1000);
        });
    }

})();                    

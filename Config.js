/**
 * Decode config files (cocos2d-js)
 * Created by Fang tianlei.
 */
(function(){
    "use strict";

    //cache configs
    var mTableDict = {};
    //configs path
    var configTables;
    //lazy config
    var lazyConfigs;
    var protoConfigs;

    var configManager = {
        init:function(cb, trigger){
            configTables = {
                MALL: "output/mall.json",
            };
            lazyConfigs = [];
            protoConfigs = [];

            var count = _.keys(configTables).length - lazyConfigs.length;
            if(count === 0){
                cb(true);
            }
            var loaded = 0;
            for(var o in configTables){
                var path = configTables[o];
                if(_.indexOf(lazyConfigs, path) === -1){
                    _loadTable(path, function(success){
                        if(success) {
                            loaded++;
                            if(loaded === count){
                                if(cb) cb(true);
                                return;
                            }
                            if(trigger) trigger(loaded * 100 / count);
                        }
                        else{
                            if(cb) cb(false);
                            return;
                        }
                    });
                }
            }
        },
        loadConfig:function(conf, cb){
            if(cc.isArray(conf)){
                var len = conf.length;
                var loaded = 0;
                for(var i = 0; i < len; i++){
                    this.loadConfig(conf[i], function(){
                        loaded++;
                        if(loaded === len){
                            cb(true);
                        }
                    });
                }
            }
            else{
                _loadTable(conf, cb)
            }
        },
        releaseConfig:function(conf){
            if(cc.isArray(conf)){
                for(var i = 0; i < conf.length; i++){
                    this.releaseConfig(conf[i]);
                }
            }
            else{
                delete mTableDict[path];
            }
        }
    };

    var _loadTable = function(path, cb) {
        if (mTableDict[path]) {
            cb(true);
            return;
        }
        cc.loader.loadBinary(path, (function (path, cb) {
            return function (error, data) {
                if (error) {
                    assert(false, "[Config ERROR] load config error.");
                }
                if(_.indexOf(protoConfigs, path) > -1) {
                    var bb = dcodeIO.ByteBuffer.wrap(data);
                    var struct = bb.readString(bb.readUint8());
                    mTableDict[path] = yc.proto[struct].decode(bb.buffer.slice(bb.offset));
                }
                else{
                    // data = utils.parseJson(cc.unzip(data));
                    data = utils.parseJson(data);
                    if(data) {
                        switch (path) {
                            case configTables.MALL:
                                mTableDict[path] = _parseMall(data);
                                break;
                            default :
                                console.logInfo("[Config] table: {0} is not exists.".format(path));
                                cb(false);
                                break;
                        }
                    }
                    else{
                        console.report("[Config] parse table: {0} error.".format(path));
                        cb(false);
                    }
                }
                cc.loader.release(path);
                cb(true);
            };
        })(path, cb));
    };
    var _parseMall = function (data) {
        var ret =[];
        for(var i = 0; i < data.length; i++){
            var ele = {};
            ele.id = data[i][0];
            ele.name = data[i][1];
            ele.goods = utils.parseItems(data[i][2]);
            ele.icon = data[i][3];
            ele.column = data[i][4];
            ele.sellType = data[i][5];
            ele.price = data[i][6];
            ele.discount = data[i][7];
            ele.limitLv = data[i][8];
            ele.productId = data[i][9];
            ele.rechargeType = data[i][10];
            ele.reward = data[i][11];
            ele.useRoomType = data[i][12];
            ele.useScenesType = data[i][13];
            ele.title = data[i][14];
            ret.push(ele);
        }
        return ret;
    };
    configManager.__defineGetter__("mall", function(){
        return mTableDict[configTables.MALL];
    });
    
    yc.config = configManager;
    yc.configTables = configTables;
    yc.lazyTables = lazyConfigs;
})();
var protobuf = require("./libs/protobuf"), ab2b = require("arraybuffer-to-buffer"), fs = require("fs"), builder = protobuf.loadProtoFile("./protobuf/index.proto"), pt = builder.build("proto"), importFiles = fs.readdirSync("./import");

importFiles.forEach(function(t) {
    var r, e, o;
    var fileName = t.split('.')[0];
    t = "./import/" + t, r = fs.readFileSync(t), e = JSON.parse(r.toString()), o = new pt[fileName](e), 
    fs.open("./output/" + fileName + ".bin", "w", function(t, r) {
        var f, i = new protobuf.ByteBuffer();
        i.writeUInt8(fileName.length), i.writeString(fileName), i.writeBytes(o.toBuffer()), 
        i.offset = 0, f = ab2b(i.buffer), fs.write(r, f, 0, f.byteLength, 0, function(t, r, e) {
            t && console.log(t);
        });
    });
});

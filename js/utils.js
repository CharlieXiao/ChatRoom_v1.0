// 定义一个工具模块

exports.cryptPwd = (password) => {
    const crypto = require('crypto');
    const md5 = crypto.createHash('md5');
    let saltPassword = password + ':' + 'charlie';
    // 加盐密码的md5值
    let result = md5.update(saltPassword).digest('hex');
    return result;
};

exports.UUID = () => {
    var d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function") {
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    return uuid;
}
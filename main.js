const electron = require("electron");
const net = require("net");
const { app, ipcMain, BrowserWindow, Menu, dialog } = electron;
const fs = require("fs")

let MainWindow;
let client_socket = new net.Socket();

let file_socket = new net.Socket();

// 保存所有窗口的数组
let windows = {}

let nowSession;

// 标准的创建窗口函数
const createWindow = exports.createWindow = (filename, window_name = null, height = 800, width = 600, parentWindow = null, message = null) => {
    let x, y;
    if (windows[window_name] != undefined) {
        windows[window_name].show()
        return windows[window_name]
    }

    const currentWindow = BrowserWindow.getFocusedWindow();　//获取当前活动的浏览器窗口。

    if (currentWindow) { //如果上一步中有活动窗口，则根据当前活动窗口的右下方设置下一个窗口的坐标
        const [currentWindowX, currentWindowY] = currentWindow.getPosition();
        x = currentWindowX + 30;
        y = currentWindowY + 30;
    }

    let newWindow = new BrowserWindow({
        x,
        y,
        show: true,
        webPreferences: {
            // WebPreferences中的nodeIntegrationInWorker选项设置为true
            nodeIntegration: true,
        },
        width: width,
        height: height,
        frame: false,
        resizable: true,
        minimizable: true,
        maximizable: false,
        parent: parentWindow,
        transparent: true,
    });　//创建新窗口，首先使用x和y坐标隐藏它。如果上一步中代码运行了，则设置这些值;如果没有运行，则未定义这些值，在这种情况下，将在默认位置创建窗口。

    Menu.setApplicationMenu(null);

    newWindow.loadFile(filename);

    // 等待窗口加载完成回调函数
    // 必须使用once，否则会出问题，将其他进程发送过来的消息也转发出去
    ipcMain.once('window-init-ready', (e, arg) => {
        e.sender.send('window-init-info', message)
    })

    //newWindow.openDevTools()

    if (window_name != null) {
        windows[window_name] = newWindow
    }

    newWindow.on('closed', () => {
        //windows.delete(newWindow);
        newWindow = null;
    });
    //windows.add(newWindow);
    return newWindow;
};

client_socket.connect(9999, '0.0.0.0');

file_socket.connect(8888,'0.0.0.0');

app.on("ready", () => {
    MainWindow = createWindow('html/login.html', null, 400, 500, null, null)
});

const sendMessageToServer = exports.sendMessageToServer = (currentWindow, msg) => {
    console.log(msg);
    client_socket.write(JSON.stringify(msg))
    if(msg['type'] == 'login'){
        // 登陆时发送给接受文件的Socket，记录响应的信息
        console.log('send message to file socket')
        file_socket.write(JSON.stringify(msg))
    }
    currentWindow.webContents.send('msg-sent', 'message send successfully')
}

const closeChildWindow = exports.closeChildWindow = (currentWindow, windowName) => {
    currentWindow.destroy()
    windows[windowName] = undefined
}

const sendFileToServer = exports.sendFileToServer = (currentWindow,from_,to_,file_path,file_name,file_type) => {
    // 尝试发送文件
    console.log('send file')
    console.log(file_path)
    console.log(file_name)
    console.log(from_)
    console.log(to_)
    let file_content = fs.readFileSync(file_path)
    let file_size = file_content.length
    console.log(file_size)
    let info = JSON.stringify({
        'from':from_,
        'to':to_,
        'file-name':file_name,
        'file-size':file_size,
        'file-type':file_type
    })
    let info_buffer = Buffer.from(info,'utf8')
    let info_length = info_buffer.length
    console.log(info_length)
    // 将length转换成二进制buffer
    let length_buffer = Buffer.alloc(8)
    // 确保长度足够
    length_buffer.writeBigUInt64BE(BigInt(info_length))
    console.log(length_buffer)
    // 拼接字符数组
    let final_buffer = Buffer.concat([length_buffer,info_buffer,file_content])
    // 发送文件
    file_socket.write(final_buffer)
}

client_socket.on('data', (data) => {
    res = JSON.parse(data)
    console.log('-----------------------------')
    console.log(res)
    console.log('-----------------------------')
    if (res['error']) {
        dialog.showMessageBoxSync(MainWindow, {
            'type': 'error',
            'title': res['error-title'],
            'message': res['error-message'],
        })
    } else {
        if (res['type'] == 'login') {
            console.log('log in successfully')
            //MainWindow.loadFile('html/home.html')
            //MainWindow.loadFile('html/home.html')
            nowSession = res['nowSession']
            let temp = MainWindow
            MainWindow = createWindow('html/home.html', null, 700, 270, null, res)
            temp.destroy()
        } else if (res['type'] == 'register') {
            windows['register'].webContents.send('msg-sent', 'register successfully')
            dialog.showMessageBoxSync(MainWindow, {
                'type': 'info',
                'message': '注册成功',
            })
            MainWindow.show()
            windows['register'].destroy()
            windows['register'] = null
        } else if (res['type'] == 'listAppend') {
            MainWindow.webContents.send('listAppend',
                {
                    'from': res['attachedMessage'],
                    'to': res['nowSession']
                })
        } else if (res['type'] == 'P2P') {
            console.log("=======================")
            console.log(res)
            console.log("=======================")
            if (windows[res['from']] == undefined) {
                // 创建窗口再发送
                windows[res['from']] = createWindow('html/chatP2P.html', res['from'], 660, 660, null, {
                    'from':res['to'],
                    'to':res['from'],
                    'text':res['text']
                })
                windows[res['from']].focus()
            }else{
                // 尝试发消息，看可不可以收到
                windows[res['from']].webContents.send('msgAppend',
                {
                    'from': res['from'],
                    'text': res['text']
                })
            }
        } else if (res['type'] == 'groupAppend') {
            console.log("=======================")
            console.log(res)
            console.log("=======================")
            MainWindow.webContents.send('groupAppend', res['group-name'])
            if(windows['createGroup'] != undefined){
                windows['createGroup'].close()
                windows['createGroup'] = undefined
            }
        } else if (res['type'] == 'Group') {
            console.log("=======================")
            console.log(res)
            console.log("=======================")
            // 必须要用户打开聊天框才可以进行聊天,group-name聊天框必须打开状态
            if(windows[res['group-name']] != undefined){
                windows[res['group-name']].webContents.send('msgAppend',
                {
                    'from': res['from'],
                    'text': res['text']
                })
            }
        }
    }
})

client_socket.on('error', () => {
    // 连接错误
    dialog.showMessageBoxSync(MainWindow, {
        'type': 'error',
        'title': '网络异常',
        'message': '无法连接服务器'
    })
    MainWindow.close()
})

//file_socket.write('hello?')

let file_buffer = undefined
let file_info = undefined
let file_length = undefined
let curr_length = undefined

file_socket.on('data',(data)=>{
    // 此处的data的最大容量为65536
    if(file_buffer == undefined){
        // 读取数据
        // 转换为数字
        let length = parseInt(data.slice(0,8).toString('hex'),16)
        console.log(length)
        file_info = JSON.parse(data.slice(8,8+length))
        console.log(file_info)
        file_buffer = data.slice(8+length)
        console.log(data.length)
        file_length = file_info['file-size']
        console.log(file_length)
        curr_length = data.length-8-length;
    }else{
        file_buffer = Buffer.concat([file_buffer,data])
        curr_length = curr_length + data.length
        if(curr_length == file_length){
            // 接受完成 
            console.log('file receviced')
            // 
            fs.writeFile('file/'+file_info['file-name'],file_buffer,(err)=>{
                // 错误回调
                if(err){
                    console.log(err)
                }
            })
            if (windows[file_info['from']] == undefined) {
                // 创建窗口再发送
                windows[file_info['from']] = createWindow('html/chatP2P.html', file_info['from'], 1200, 1500, null, {
                    'from':file_info['to'],
                    'to':file_info['from'],
                    'fileName':file_info['file-name'],
                    // 相对于html的路径
                    'filePath':'../file/'+file_info['file-name'],
                    'fileType':file_info['file-type']
                })
                windows[file_info['from']].focus()
            }else{
                // 尝试发消息，看可不可以收到
                windows[file_info['from']].webContents.send('fileRecv',
                {
                    'from': file_info['from'],
                    'fileName':file_info['file-name'],
                    // 相对于html的路径
                    'filePath':'../file/'+file_info['file-name'],
                    'fileType':file_info['file-type']
                })
            }
            console.log('file saved')
            file_buffer = undefined
            file_info = undefined
            file_length = undefined
            curr_length = undefined
        }
    }
})

file_socket.on('error',()=>{
    MainWindow.close()
})


// 打开文件选择菜单
//console.log(dialog.showOpenDialog({ properties: [ 'openFile', 'openDirectory', 'multiSelections' ]}));


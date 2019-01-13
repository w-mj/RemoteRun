# Remote Run

可以瞬间将控制台程序变成网络程序，即将控制台的输入输出以原始字节流或websocket方式映射到网络流。

## 使用说明

usage: main.py \[-h\] \[-a ADDRESS\] \[-s\] \[-m {socket,websocket,http}\] task

positional arguments:
  task                  要执行的任务

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        本地服务器监听地址 ip:port
  -s, --autostart       任务结束后是否自动重新启动
  -m {socket,websocket,http}, --method {socket,websocket,http}
                        指定以socket、websocket或http方式传输信息，默认为socket。


当以socket或websocket运行时，其他程序建立连接后可以直接通信。
当以http方式运行时，仅接收POST请求，输入数据和返回结果均以raw方式保存在请求和返回的data域中。

## Reference
+ [Windows Python select标准输入输出](http://www.ideawu.net/blog/archives/508.html)
+ [websocket](http://python.jobbole.com/88207/)
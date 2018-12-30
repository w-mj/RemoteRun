# Remote Run

可以瞬间将控制台程序变成网络程序，即将控制台的输入输出流映射到socket。

## 使用说明

usage: server.py \[-h\] \[-a ADDRESS\] \[-s\] task

positional arguments:
  task                  要执行的任务

optional arguments:
  -h, --help            show this help message and exit
  -a , --address ADDRESS  本地服务器监听地址 ip:port
  -s, --autostart       任务结束后是否自动重新启动



运行本程序将产生一个socket服务，其他程序连接后即可直接交互。



## TODO:

+ websocket
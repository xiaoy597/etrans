安装配置说明
============

1、安装

以root用户执行以下操作：
a) 创建/usr/local/etrans目录，在该目录下创建bin, log, etc子目录。
b) 将doc-sync.py拷贝到/usr/local/etrans/bin目录下。
c) 将conf.ini拷贝到/usr/local/etrans/etc目录下。
d) 将doc-sync文件拷贝到/etc/init.d目录下。
e) 执行以下命令
	ln -s /etc/init.d/doc-sync /etc/rc3.d/S98doc-sync
	ln -s /etc/init.d/doc-sync /etc/rc5.d/S98doc-sync

2、配置

打开/usr/local/etrans/etc/conf.ini文件，根据具体运行环境设置以下参数，

SourceDirectory		文件同步源路径
TargetDirectory		文件同步目标路径

DatabaseServer		数据库服务器名称/IP
DatabaseName		文件共享日志表所在库名
DatabaseUser		数据库用户名
DatabasePass		数据库用户口令

3、服务的启动、停止和重启

默认安装情况下，服务会自动随操作系统启动。以root用户执行以下命令对服务进行手工操作，

启动服务：
	/etc/init.d/doc-sync start
停止服务：
	/etc/init.d/doc-sync stop
重启服务：
	/etc/init.d/doc-sync restart

程序执行日志在/usr/local/etrans/log目录下。


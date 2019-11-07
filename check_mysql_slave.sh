#!/bin/bash
# more check_mysql_slave.sh
# 监控 Slave 状态并邮件通知
DBUSR="root"
DBPWD="xxxx"
MailList=abc@abc.com
HostName="127.0.0.1"

YES=`/usr/bin/mysql -u$DBUSR -p$DBPWD -e 'show slave status\G'  2>&1 |grep -E "Slave_IO_Running|Slave_SQL_Running"|awk '{print $2}'|grep -c Yes|grep -v ^Warning`

if [ $YES -ne 2 ];then
 	echo "$HostName Slave stopped `date +"%R %F"`" | muttr -s "Warning:$HostName  Mysql-Slave stopped!!!" $MailList
fi

exit 0
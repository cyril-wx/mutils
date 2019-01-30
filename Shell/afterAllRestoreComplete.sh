#!/bin/bash
# 本脚本用于检测刷机是否完成，如果完成继续下一步命令，如果未完成则退出。
parent_path="/Users/gdlocal/Library/Application Support/PurpleRabbit/Logs"
log_filename="host.log"
skey="0x1A*"

cd "$parent_path"
cable_id=`find . -iname "$skey" -maxdepth 1`  # Only find current dir.
#cable_id_1="$cable_id[0]"
#cable_id_2="$cable_id[1]"

checkHostLog(){

if [ $# -ne 1 ];then
        echo ' Error params. Usage : ./checkHostLogResult.sh "./host.log" '
        return -1
fi

host_log="$1"
if [ ! -f "$host_log" ]; then
        echo "host_log file is not exists, maybe restore failed."
        return -1
fi

result=`tail -n -2 "$host_log" | sed '$d' | cut -d "]" -f 2 | sed 's/^[ \t]*//g' | sed 's/[ \t]*$//g'`
echo $result
if [ "$result"x=="Successfully restored"x ];then
	continue
else:
        exit -1  # Failure
fi

}

checkFileChanged(){
file_path=$1
path=${file_path%/*}
cd "$path"
file=${file_path##*/}
if [ -f $file ]
then
        cat $file > /tmp/$file.ori
        file1=/tmp/$file.ori
        sleep 5
        file2=$file
        diff $file1 $file2 > /dev/null
        if [ $? != 0 ]
        then
                echo "Diffe"
        else
                echo "Same"
        fi
else
        #echo "$file  does not exist, please check filename."
	echo "None"
fi
rm -rf /tmp/$file.ori
}

for item in $cable_id
do
	echo "Check logs for $item" 
	current_log_path="$parent_path/$item"
#	echo "current_log_path = $current_log_path"
	if [ ! -d "$current_log_path" ]; then
        	echo "$cable_id's log folder is not exists, maybe restore failed."
        	exit -1
	fi
	cd "$current_log_path"

	logs_sub_path=`find . -name "$log_filename"`
	logs_complete_path="$current_log_path/$logs_sub_path"
#	echo "logs_complete_path = $logs_complete_path"
	
	res=`checkFileChanged "$logs_complete_path"`

	if [ "$res" = "Diffe" ] || [ "$res" = "None" ];then
		echo "$item imcomplete" # restore complete
		exit 1	# restore not complete.
	elif [ "$res" = "Same" ];then
		echo "$item OK" # restore complete
	fi
done

echo "All restore complete"

/Users/gdlocal/Desktop/manual_write_pass_record add_bobcat G6TY100TLV6V
/Users/gdlocal/Desktop/manual_write_pass_record add_bobcat G6TY100TLV6V
/Users/gdlocal/Desktop/BYSerial

exit 0

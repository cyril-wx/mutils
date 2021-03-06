#!/bin/bash

"""
#修改PR中PostRestore/Bundle的值
# @Author: Cyril.J
# @Dep: SW-CoreOS
# @Date: 2019-11-27
"""


puplerabbit_pr_path="/Users/gdlocal/Library/Application Support/PurpleRabbit/pr"
puplerestore_pr_path="/Users/gdlocal/Library/Application Support/PurpleRestore"

p2_pr_file_nums=`ls "$puplerabbit_pr_path" | grep "DEVELOPMENT.*.pr" | wc -l | awk '$1=$1'`
ramdisk_pr_file_nums=`ls "$puplerabbit_pr_path" | grep "FACTORYRAMDISK.pr" | wc -l | awk '$1=$1'`

echo "p2_pr_file_nums=$p2_pr_file_nums"
echo "ramdisk_pr_file_nums=$ramdisk_pr_file_nums"

modifyValueAndRewrite(){
	filePath=$1
	echo "
		filepath=${filePath}
	"

#	cat "${filePath}"
	
	tag_postrestoreaction=0
	tag_bundlepath=0
	bak=$IFS     #定义一个变量bak保存IFS的值
	IFS=$'\n'    #将环境变量IFS的值修改为换行符
	for line in `cat "${filePath}"`
#	while read line
	do
	echo "# "$line
	hline=`echo $line | awk '$1=$1'`
	if [ ${tag_postrestoreaction} -eq 1 ]; then
		echo "rewrite 1#"
		line="		<string>Reboot</string>"
		tag_postrestoreaction=0
	elif [ ${tag_bundlepath} -eq 1 ]; then
		echo "rewrite 2#"
		line="		<string>/Users/gdlocal/RestorePackage/CurrentBundle/Restore</string>"
		tag_bundlepath=0
	elif [ "${hline}" = "<key>PostRestoreAction</key>" ]; then
		echo "hello PostRestoreAction"
		tag_postrestoreaction=1
	elif [ "${hline}" = "<key>RestoreBundlePath</key>"  ]; then
		echo "hello BundlePath"
		tag_bundlepath=1
	fi
	echo "${line}" >> "${filePath}.tmp"
#	done < "${filePath}"
	done
	rm -f "${filePath}"; mv "${filePath}.tmp" "${filePath}";
}


if [ "${p2_pr_file_nums}" != '' ] && [ ${p2_pr_file_nums} -gt 0 ] && [ "${ramdisk_pr_file_nums}" = '1' ];then
	echo "exists"
	exit 0
else
	echo "not exists"
	cp -rf ~/Library/Application\ Support/PurpleRestore/*.pr  "${puplerabbit_pr_path}/" 
	modifyValueAndRewrite "${puplerabbit_pr_path}/DEVELOPMENT-PROV.pr" 
	modifyValueAndRewrite "${puplerabbit_pr_path}/DEVELOPMENT-PROV_ap.pr" 

fi


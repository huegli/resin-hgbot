#!/bin/bash

# stop unnecessary stuff
 systemctl stop spacenavd

# Enable PS4 bluetooth
hciconfig hciX up

echo 127.0.0.1 `hostname` >> /etc/hosts

#Set the root password
# echo "root:$PASSWD" | chpasswd

# Start up the ROS server
source /opt/ros/kinetic/setup.bash
cd /ros/hgbot_ws/src/hgbot_infra
git pull
cd /ros/hgbot_ws
catkin_make

# Launch FTP server
python -m pyftpdlib -w &

# Launch PS4 driver
ds4drv &

roscore
#while :
#do
#    curl -X GET --header "Content-Type:application/json" \
#        "$RESIN_SUPERVISOR_ADDRESS/ping?apikey=$RESIN_SUPERVISOR_API_KEY"
#    sleep 60
#done

# sleep 3
# avahi-browse -a | grep IPv4

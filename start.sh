#!/bin/bash

# stop unnecessary stuff
# systemctl stop spacenavd

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
apt-get update
rosdep update
rosdep install --from-paths src --ignore-src -r -y
catkin_make
source /ros/hgbot_ws/devel/setup.bash

echo "source /opt/ros/kinetic/setup.bash" > setup
echo "source /ros/hgbot_ws/devel/setup.bash" >> setup 
chmod +x setup

echo "rosservice call bt_joy_service scan" > pair
chmod +x pair

# Launch FTP server
python -m pyftpdlib -w -p 21 &

# Launch ROS
echo "Launching ROS Core & nodes"
#roscore &
#rosrun hgbot_infra bt_joy
roslaunch hgbot_infra hgbot_infra.launch

# Launch PS4 driver
### sleep 10
### # ds4drv &
### 
### while :
### do
###     curl -X GET --header "Content-Type:application/json" \
###         "$RESIN_SUPERVISOR_ADDRESS/ping?apikey=$RESIN_SUPERVISOR_API_KEY"
###     echo "Hello ROS"
###     sleep 60
### done

# sleep 3
# avahi-browse -a | grep IPv4

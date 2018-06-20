#!/bin/bash

# stop unnecessary stuff
systemctl stop spacenavd
systemctl stop bluetooth

echo 127.0.0.1 `hostname` >> /etc/hosts

# cd ~
# 
# git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
# git clone https://github.com/morhetz/gruvbox.git ~/.vim/bundle/gruvbox
# git clone https://github.com/huegli/dotfiles
# ln -s dotfiles/vimrc .vimrc
# ln -s dotfiles/dir_colors .dir_colors
# ln -s dotfiles/tmux.conf .tmux.conf
# echo "source /ros/hgbot_ws/devel/setup.bash" >> ~/.bashrc
# echo "export TERM=xterm-256color" >> ~/.bashrc

# export TERM=xterm-256color
# vim +PluginInstall +qall


#Set the root password as root if not set as an ENV variable
export PASSWD=${PASSWD:=root}
#Set the root password
echo "root:$PASSWD" | chpasswd

# Start up the ROS server
source /opt/ros/kinetic/setup.bash
cd /ros/hgbot_ws/src/hgbot_infra
git pull
cd /ros/hgbot_ws
catkin_make

roscore
#while :
#do
#    curl -X GET --header "Content-Type:application/json" \
#        "$RESIN_SUPERVISOR_ADDRESS/ping?apikey=$RESIN_SUPERVISOR_API_KEY"
#    sleep 60
#done

# sleep 3
# avahi-browse -a | grep IPv4

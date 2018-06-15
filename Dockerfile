FROM resin/rpi-raspbian:jessie

#switch on systemd init system in container
ENV INITSYSTEM on
# expose DBUS insid container
ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

RUN echo "deb http://packages.ros.org/ros/ubuntu xenial main" > /etc/apt/sources.list.d/ros-latest.list
RUN apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-key 421C365BD9FF1F717815A3895523BAEEB01FA116
RUN apt-get update && apt-get -y install python-rosdep python-rosinstall-generator python-wstool python-rosinstall build-essential cmake python-pip wget unzip vim-nox git tmux avahi-utils libnss-mdns openssh-server

COPY catkin_ws /ros/catkin_ws
WORKDIR /ros/catkin_ws

# Install ROS following instructions here:
# http://wiki.ros.org/ROSberryPi/Installing%20ROS%20Kinetic%20on%20the%20Raspberry%20Pi
RUN rosinstall_generator ros_comm ros_control rosbridge_suite joystick_drivers teleop_twist_joy --rosdistro kinetic --deps --wet-only --tar > kinetic-ros_custom-wet.rosinstall
RUN wstool init src kinetic-ros_custom-wet.rosinstall
WORKDIR /ros/catkin_ws/external_src
RUN unzip assimp-3.1.1_no_test_models.zip
WORKDIR /ros/catkin_ws/external_src/assimp-3.1.1
RUN cmake . && make && make install
WORKDIR /ros/catkin_ws
RUN rosdep init && rosdep update
RUN rosdep install -y --from-paths src --ignore-src --rosdistro kinetic -r --os=debian:jessie
RUN ./src/catkin/bin/catkin_make_isolated --install -DCMAKE_BUILD_TYPE=Release --install-space /opt/ros/kinetic
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# here we set up the config for openSSH.
RUN mkdir /var/run/sshd \
    && sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config

# set up dev environment
WORKDIR /root
RUN git clone https://github.com/VundleVim/Vundle.vim.git /root/.vim/bundle/Vundle.vim
RUN git clone https://github.com/morhetz/gruvbox.git /root/.vim/bundle/gruvbox
RUN git clone https://github.com/huegli/dotfiles
RUN ln -s dotfiles/vimrc .vimrc
RUN ln -s dotfiles/dir_colors .dir_colors
RUN ln -s dotfiles/tmux.conf .tmux.conf
RUN echo "export TERM=xterm-256color" >> ~/.bashrc

# Set up HGBot workspace
RUN mkdir -p /ros/hgbot_ws/src
WORKDIR /ros/hgbot_ws/src
RUN git clone https://github.com/huegli/hgbot_infra.git
RUN git config --global user.email "nikolai.schlegel@gmail.com"
RUN git config --global user.name  "Nikolai Schlegel"
RUN git config --global push.default simple
WORKDIR /ros/hgbot_ws
RUN /opt/ros/kinetic/bin/catkin_make
RUN echo "source /opt/ros/kinetic/setup.bash" >> /root/.bashrc
RUN echo "source /ros/hgbot_ws/devel/setup.bash" >> /root/.bashrc

COPY start.sh /ros/start.sh

CMD [ "/bin/bash", "/ros/start.sh" ]

#!/usr/bin/env bash

# install basic env
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential git curl wget

# install oh-my-zsh
sudo apt install -y zsh
sh ./install-oh-my-zsh.sh
export ZSH_CUSTOM=~/.oh-my-zsh/custom
git clone https://gitee.com/mirror-github/zsh-autosuggestions.git $ZSH_CUSTOM/plugins/zsh-autosuggestions
git clone https://gitee.com/mirror-github/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
sed -i 's/^ZSH_THEME=.*/ZSH_THEME="ys"/g' ~/.zshrc
sed -i 's/^plugins=.*/plugins=\(git zsh-autosuggestions zsh-syntax-highlighting\)/g' ~/.zshrc

# install Java and Maven
sudo apt install -y openjdk-8-jdk maven
mkdir ~/.m2
cat >~/.m2/settings.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
    <mirrors>
        <mirror>
            <id>alimaven</id>
            <name>aliyun maven</name>
            <url>http://maven.aliyun.com/nexus/content/groups/public/</url>
            <mirrorOf>central</mirrorOf>
        </mirror>
    </mirrors>
</settings>
EOF
echo >>~/.zshrc "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64"

# install Python
sudo apt install -y python3 python3-pip python3-dev
mkdir ~/.pip
cat >~/.pip/pip.conf <<EOF
[global]
index-url = http://mirrors.aliyun.com/pypi/simple/

[install]
trusted-host = mirrors.aliyun.com
EOF

# install vim
sudo apt install -y vim
mkdir -p ~/.vim/autoload ~/.vim/bundle
cp ./pathogen.vim ~/.vim/autoload/pathogen.vim
cat >~/.vimrc <<EOF
set tabstop=4
set softtabstop=4
set shiftwidth=4
set autoindent
set smartindent

set fileencodings=utf-8,gbk

autocmd FileType python set expandtab

execute pathogen#infect()
syntax on
filetype plugin indent on
EOF

#!/bin/bash

# 检查是否提供了 Home Assistant 配置目录作为参数
if [ $# -ne 1 ]; then
    echo "用法: $0 <Home Assistant 配置目录>"
    exit 1
fi

# 获取 Home Assistant 配置目录
CONFIG_DIR="$1"

# 源目录
SOURCE_DIR="$(dirname "$0")/custom_components/wisecloud_home"

# 目标目录
DEST_DIR="$CONFIG_DIR/custom_components/wisecloud_home"

# 检查源目录是否存在
if [ ! -d "$SOURCE_DIR" ]; then
    echo "错误: 源目录 $SOURCE_DIR 不存在。"
    exit 1
fi

# 创建目标目录（如果不存在）
mkdir -p "$(dirname "$DEST_DIR")"

# 复制文件
echo "正在将云鹿智能门集成复制到 $DEST_DIR..."
cp -r "$SOURCE_DIR" "$DEST_DIR"

# 检查复制是否成功
if [ $? -eq 0 ]; then
    echo "安装成功！云鹿智能门集成已复制到 $DEST_DIR。"
else
    echo "错误: 安装过程中出现问题。请检查权限或重试。"
    exit 1
fi
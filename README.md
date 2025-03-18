# 云鹿智能门 Home Assistant 集成说明

云鹿智能门集成是一个专为 Home Assistant 打造的组件，借助此集成，您能够在 Home Assistant 生态系统内便捷操控云鹿智能门设备，极大提升智能家居的联动体验。

## 安装

### Home Assistant 版本要求：

Core ≥ 2024.4.4

Operating System ≥ 13.0

### 方法 1：使用 git clone 命令从 GitHub 下载

进入 Home Assistant 配置目录：



```
cd config
```

克隆云鹿智能门集成仓库：



```
git clone https://github.com/wisedeer2022/ha_wisecloud_home.git
```

进入克隆后的目录并执行安装脚本：



```
cd ha_wisecloud_home

./install.sh /config
```

此方法推荐使用，如需更新至特定版本，切换至相应的 Tag 即可。例如，更新至 v2.0.0 版本：



```
cd config/ha_wisecloud_home

git fetch

git checkout v2.0.0

./install.sh /config
```

### 方法 2: HACS

打开 HACS，点击右上角三个点。

选择 “Custom repositories”。

在 “Repository” 处填写：[https://github.com/wisedeer2022/ha_wisecloud_home.git](https://github.com/wisedeer2022/ha_wisecloud_home.git) ，“Category or Type” 选择：Integration ，然后点击 “ADD”。

点击 HACS 的 “New” 或 “Available for download” 分类下的 “Wisecloud Home”，进入集成详情页，点击 “DOWNLOAD”。

目前云鹿智能门集成暂未添加到 HACS 商店，敬请关注后续更新。

### 方法 3：通过 Samba 或 FTPS 手动安装

下载 custom\_components/wisecloud\_home 文件夹。

将下载的文件夹复制到 Home Assistant 的 config/custom\_components 文件夹下。

## 配置

**登录**：

进入 Home Assistant 设置 > 设备与服务 > 添加集成。

**搜索与添加**：

搜索 “Wisecloud Home”，点击下一步。

**账户登录**：

点击相应登录提示，使用云鹿智能门关联的账号登录。

登录成功后，您就可以在 Home Assistant 中对云鹿智能门进行各种设置与自动化联动，畅享智能门带来的便捷与安全。

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=wisecloud_home)
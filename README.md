# watercooler-manager-ha插件（全部由OpenAI完成）
水冷设备的 Home Assistant 自定义集成

## 项目依赖
- https://github.com/shipkjzy/watercooler-manager

## HA 安装方式
- 解压 watercooler_manager_ha_custom_component.zip
- 把里面的文件夹放到 HA：
- /config/custom_components/watercooler_manager/
- 重启 Home Assistant
  
## 水冷程序里勾选：
- 启用 API
- 默认端口：21977

## HA 里添加集成：
- 设置 → 设备与服务 → 添加集成 → Watercooler Manager
- 主机地址填运行水冷程序那台 Windows 电脑的局域网 IP，例如：192.168.1.50
- /config/custom_components/watercooler_manager/
- 重启 Home Assistant

## 也可以先在 HA 所在设备浏览器访问测试：
- http://电脑IP:21977/api/status

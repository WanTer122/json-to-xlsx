# JSON → Excel 转换工具

将 JSON 数据转换为 Excel（.xlsx）的 Windows 桌面应用，支持字段映射、多 Sheet 拆分、数据预览等功能。

## 使用流程

1. 解压收到的 `JSON转Excel.zip`
2. 进入 `JSON转Excel` 文件夹
3. 双击 `JSON转Excel.exe` 启动

> **注意**：请保持文件夹内所有文件完整，不要只复制 exe 文件。

### 系统要求

- Windows 10 / 11（64 位）
- 无需安装 Python



打包完成后，产物位于 `dist\JSON转Excel\`，将整个文件夹压缩分享给他人即可。


## 功能说明

- 粘贴或上传 JSON 文件
- 自动识别字段并转换为中文列名
- 自定义列名映射
- 按字段拆分为多个 Sheet
- 生成前预览数据
- 导出为 `.xlsx` 文件

## 项目结构

```
json-to-xlsx/
├── app.py              # 主程序
├── converter.py        # 转换逻辑
├── dialogs.py          # 对话框
├── assets/             # 图标与主题
├── json-to-xlsx.spec   # PyInstaller 配置
├── build.bat           # 一键打包脚本
├── requirements.txt    # Python 依赖
└── launch.vbs          # 开发时启动（无黑窗口）
```

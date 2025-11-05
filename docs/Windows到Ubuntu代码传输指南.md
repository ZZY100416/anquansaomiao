# Windows到Ubuntu代码传输指南

## 📋 方法概览

根据您的虚拟化软件和网络环境，选择最适合的方法：

| 方法 | 适用场景 | 难度 | 速度 |
|------|---------|------|------|
| 共享文件夹 | VirtualBox/VMware | ⭐ 简单 | 快 |
| SCP/SSH | 已配置SSH | ⭐⭐ 中等 | 中等 |
| Git推送 | 已配置GitHub | ⭐ 简单 | 快 |
| U盘/移动设备 | 物理设备 | ⭐ 简单 | 慢 |
| 网络共享 | 局域网 | ⭐⭐ 中等 | 中等 |

## 🚀 方法1: 共享文件夹（推荐 - VirtualBox/VMware）

### VirtualBox 共享文件夹

#### 步骤1: 在VirtualBox中配置共享文件夹

1. **关闭Ubuntu虚拟机**（如果正在运行）

2. **右键虚拟机 → 设置 → 共享文件夹**

3. **添加共享文件夹**:
   - 点击右侧的"+"按钮
   - **文件夹路径**: 选择 `E:\network\anquannchanpin`
   - **文件夹名称**: `unified-security-scanner`（或任意名称）
   - **只读**: 取消勾选（允许读写）
   - **自动挂载**: ✅ 勾选
   - **固定分配**: ✅ 勾选

4. **点击"确定"保存**

#### 步骤2: 在Ubuntu中安装增强功能

```bash
# 启动Ubuntu虚拟机

# 安装必要的工具
sudo apt update
sudo apt install -y build-essential dkms linux-headers-$(uname -r)

# 在VirtualBox菜单中: 设备 → 安装增强功能
# 或者手动挂载
sudo mount /dev/cdrom /mnt
cd /mnt
sudo ./VBoxLinuxAdditions.run

# 重启虚拟机
sudo reboot
```

#### 步骤3: 访问共享文件夹

```bash
# 共享文件夹通常在 /media/sf_文件夹名称
# 如果没有自动挂载，手动挂载：
sudo mkdir -p /mnt/shared
sudo mount -t vboxsf unified-security-scanner /mnt/shared

# 将当前用户添加到vboxsf组（以便访问共享文件夹）
sudo usermod -aG vboxsf $USER

# 重新登录或执行
newgrp vboxsf

# 验证访问
ls -la /media/sf_unified-security-scanner
# 或
ls -la /mnt/shared
```

#### 步骤4: 复制代码到项目目录

```bash
# 创建项目目录
mkdir -p ~/projects
cd ~/projects

# 复制代码（从共享文件夹）
cp -r /media/sf_unified-security-scanner/* ./unified-security-scanner/
# 或
cp -r /mnt/shared/* ./unified-security-scanner/

# 进入项目目录
cd unified-security-scanner

# 验证文件
ls -la
```

### VMware 共享文件夹

#### 步骤1: 在VMware中配置共享文件夹

1. **虚拟机 → 设置 → 选项 → 共享文件夹**

2. **添加共享文件夹**:
   - 点击"添加"
   - 选择 `E:\network\anquannchanpin`
   - 启用共享
   - 完成

#### 步骤2: 在Ubuntu中访问

```bash
# VMware共享文件夹通常在 /mnt/hgfs
ls -la /mnt/hgfs/

# 如果看不到，安装VMware Tools
sudo apt install -y open-vm-tools
sudo reboot

# 复制代码
mkdir -p ~/projects/unified-security-scanner
cp -r /mnt/hgfs/anquannchanpin/* ~/projects/unified-security-scanner/
```

## 🔐 方法2: SCP/SSH传输（推荐 - 如果已配置SSH）

### 步骤1: 在Ubuntu上启用SSH

```bash
# 在Ubuntu虚拟机中执行
sudo apt update
sudo apt install -y openssh-server

# 启动SSH服务
sudo systemctl start ssh
sudo systemctl enable ssh

# 查看IP地址
ip addr show
# 或
hostname -I
```

### 步骤2: 在Windows上使用SCP传输

#### 使用PowerShell（Windows 10+）

```powershell
# 打开PowerShell（管理员权限）

# 进入项目目录
cd E:\network\anquannchanpin

# 使用scp传输（替换为您的Ubuntu IP和用户名）
scp -r * ubuntu-user@192.168.1.100:/home/ubuntu/projects/unified-security-scanner/

# 如果需要指定SSH密钥
scp -i C:\path\to\private_key -r * ubuntu-user@192.168.1.100:/home/ubuntu/projects/unified-security-scanner/
```

#### 使用WinSCP（图形界面工具）

1. **下载安装WinSCP**: https://winscp.net/

2. **连接Ubuntu**:
   - 主机名: Ubuntu的IP地址（如 `192.168.1.100`）
   - 用户名: ubuntu用户名
   - 密码: ubuntu密码
   - 端口: 22

3. **传输文件**:
   - 左侧：Windows文件（E:\network\anquannchanpin）
   - 右侧：Ubuntu目录（/home/ubuntu/projects/unified-security-scanner）
   - 拖拽文件或使用复制按钮

#### 使用PuTTY/PSFTP

```powershell
# 使用PSFTP（PuTTY工具包的一部分）
psftp ubuntu-user@192.168.1.100

# 连接后执行
cd /home/ubuntu/projects
mkdir unified-security-scanner
cd unified-security-scanner
lcd E:\network\anquannchanpin
put -r *
```

## 🌐 方法3: Git推送（最推荐 - 如果已配置GitHub）

### 步骤1: 在Windows上提交并推送到GitHub

```powershell
# 在Windows PowerShell中执行
cd E:\network\anquannchanpin

# 检查Git状态
git status

# 如果还没初始化Git
git init
git add .
git commit -m "feat: 初始提交 - 统一安全扫描平台"

# 添加远程仓库（在GitHub上创建仓库后）
git remote add origin https://github.com/your-username/unified-security-scanner.git
# 或使用SSH
git remote add origin git@github.com:your-username/unified-security-scanner.git

# 推送代码
git branch -M main
git push -u origin main
```

### 步骤2: 在Ubuntu上克隆代码

```bash
# 在Ubuntu虚拟机中执行

# 安装Git（如果还没安装）
sudo apt install -y git

# 配置Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 生成SSH密钥（如果还没生成）
ssh-keygen -t ed25519 -C "your.email@example.com"
# 按回车使用默认路径
cat ~/.ssh/id_ed25519.pub
# 复制公钥，添加到GitHub: https://github.com/settings/keys

# 克隆代码
mkdir -p ~/projects
cd ~/projects
git clone git@github.com:your-username/unified-security-scanner.git
# 或使用HTTPS
git clone https://github.com/your-username/unified-security-scanner.git

cd unified-security-scanner

# 验证文件
ls -la
```

## 💾 方法4: U盘/移动设备

### 步骤1: 在Windows上复制到U盘

1. 插入U盘
2. 复制 `E:\network\anquannchanpin` 整个文件夹到U盘

### 步骤2: 在Ubuntu中挂载U盘

```bash
# 插入U盘后，查看设备
lsblk

# 挂载U盘（假设是/dev/sdb1）
sudo mkdir /mnt/usb
sudo mount /dev/sdb1 /mnt/usb

# 复制文件
mkdir -p ~/projects/unified-security-scanner
cp -r /mnt/usb/anquannchanpin/* ~/projects/unified-security-scanner/

# 卸载U盘
sudo umount /mnt/usb
```

## 📁 方法5: Windows网络共享（Samba）

### 步骤1: 在Windows上设置共享

1. **右键项目文件夹** `E:\network\anquannchanpin`
2. **属性 → 共享 → 高级共享**
3. **勾选"共享此文件夹"**
4. **设置共享名称**: `unified-security-scanner`
5. **权限**: 添加Everyone，设置读取权限
6. **确定**

### 步骤2: 在Ubuntu中访问

```bash
# 安装Samba客户端
sudo apt install -y cifs-utils

# 创建挂载点
sudo mkdir /mnt/windows-share

# 挂载共享文件夹（替换为Windows IP和用户名）
sudo mount -t cifs //192.168.1.50/unified-security-scanner /mnt/windows-share \
  -o username=windows-username,password=windows-password

# 复制文件
mkdir -p ~/projects/unified-security-scanner
cp -r /mnt/windows-share/* ~/projects/unified-security-scanner/

# 卸载
sudo umount /mnt/windows-share
```

## ✅ 推荐方案对比

### 方案A: 使用共享文件夹（最简单）

**优点**:
- ✅ 设置简单
- ✅ 实时同步（修改后立即可见）
- ✅ 不需要网络

**缺点**:
- ❌ 需要安装增强功能
- ❌ 性能可能略慢

**适用**: VirtualBox/VMware用户

### 方案B: 使用Git推送（最推荐）

**优点**:
- ✅ 版本控制
- ✅ 可以回滚
- ✅ 团队协作
- ✅ 代码备份

**缺点**:
- ❌ 需要配置GitHub
- ❌ 需要网络连接

**适用**: 所有用户，特别是需要版本控制的场景

### 方案C: 使用SCP/SSH（最灵活）

**优点**:
- ✅ 安全传输
- ✅ 可以脚本化
- ✅ 适合大文件

**缺点**:
- ❌ 需要配置SSH
- ❌ 需要网络连接

**适用**: 已熟悉SSH的用户

## 🎯 快速操作指南

### 如果您使用VirtualBox（推荐）

```bash
# 1. 在VirtualBox中配置共享文件夹（通过图形界面）
#    路径: E:\network\anquannchanpin
#    名称: unified-security-scanner

# 2. 在Ubuntu中安装增强功能
sudo apt install -y build-essential dkms
# 然后: 设备 → 安装增强功能

# 3. 添加用户到vboxsf组
sudo usermod -aG vboxsf $USER
# 重新登录

# 4. 复制代码
mkdir -p ~/projects
cp -r /media/sf_unified-security-scanner/* ~/projects/unified-security-scanner/
cd ~/projects/unified-security-scanner
```

### 如果您使用GitHub（最推荐）

```powershell
# Windows PowerShell
cd E:\network\anquannchanpin
git init
git add .
git commit -m "feat: 初始提交"
git remote add origin https://github.com/your-username/unified-security-scanner.git
git push -u origin main
```

```bash
# Ubuntu
cd ~/projects
git clone https://github.com/your-username/unified-security-scanner.git
cd unified-security-scanner
```

## 🔍 验证传输

无论使用哪种方法，传输后验证：

```bash
# 进入项目目录
cd ~/projects/unified-security-scanner

# 检查关键文件
ls -la docker-compose.yml
ls -la backend/
ls -la frontend/
ls -la .github/

# 检查文件数量
find . -type f | wc -l

# 检查Git状态（如果使用Git）
git status
```

## ❓ 常见问题

### Q1: 共享文件夹看不到怎么办？

**A**: 
```bash
# 检查是否安装了增强功能
lsmod | grep vboxsf

# 如果没有，安装增强功能
sudo apt install -y virtualbox-guest-dkms virtualbox-guest-utils
sudo reboot

# 手动挂载
sudo mount -t vboxsf 共享文件夹名称 /mnt/shared
```

### Q2: SCP连接被拒绝？

**A**:
```bash
# 在Ubuntu中检查SSH服务
sudo systemctl status ssh

# 如果没有运行，启动
sudo systemctl start ssh
sudo systemctl enable ssh

# 检查防火墙
sudo ufw status
sudo ufw allow 22
```

### Q3: Git克隆失败？

**A**:
```bash
# 检查网络连接
ping github.com

# 检查SSH密钥
ssh -T git@github.com

# 如果使用HTTPS，检查凭据
git config --global credential.helper store
```

### Q4: 文件权限问题？

**A**:
```bash
# 修复文件权限
cd ~/projects/unified-security-scanner
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;
chmod +x *.sh  # 如果有脚本文件
```

## 📝 下一步

传输完成后：

1. **验证文件完整性**
2. **初始化Git仓库**（如果还没初始化）
3. **启动Docker服务**: `docker-compose up -d`
4. **初始化数据库**: `docker-compose exec backend python init_db.py`
5. **访问Web界面**: http://localhost:3000

---

**推荐**: 如果您是第一次传输，建议使用**Git方法**，这样代码可以版本控制，也方便后续协作。

如果需要帮助，请告诉我您使用的是哪种虚拟化软件（VirtualBox/VMware），我可以提供更详细的指导。


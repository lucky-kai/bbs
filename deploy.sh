# 遇到错误马上停下来
# 显示执行哪一行
set -ex

# 系统设置
apt-get -y install zsh curl ufw
ufw allow 22
ufw allow 80
ufw allow 443
ufw default deny incoming
ufw default allow outgoing
ufw status verbose
ufw -f enable

# 装依赖
apt-get update
# 安装过程中选择默认选项，这样不会弹出 libssl 确认框
export DEBIAN_FRONTEND=noninteractive
apt-get install -y git nginx mysql-server python3-pip
pip3 install jinja2 flask gunicorn pymysql flask_sqlalchemy flask_admin flask_mail marrow.mailer

# 删除测试用户和测试数据库并限制关闭公网访问
# 记得换密码
mysql -u root -pzaoshuizaoqi -e "DELETE FROM mysql.user WHERE User='';"
mysql -u root -pzaoshuizaoqi -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
mysql -u root -pzaoshuizaoqi -e "DROP DATABASE IF EXISTS test;"
mysql -u root -pzaoshuizaoqi -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
# 设置密码并切换成密码验证
mysql -u root -pzaoshuizaoqi -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'zaoshuizaoqi';"

# 删掉 nginx default 设置
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-available/default
# nginx
# 不要在 sites-available 里面放任何东西
cp bbs.nginx /etc/nginx/sites-enabled/bbs

# systemd bbs python 服务
cp bbs.service /etc/systemd/system/bbs.service

# 重启服务器
systemctl daemon-reload
systemctl restart bbs
systemctl restart nginx

# 初始化数据
python3 reset.py
# 测试本地访问
curl http://localhost
echo 'deploy success'
# django-switch-config-backup

An extension to switchinfo to backup switch config with version control using git

# Setup

* Add to INSTALLED_APPS: `config_backup.apps.ConfigBackupConfig`
* Set BACKUP_PATH to the git repository. There should be a parent folder that can be set as the root for gitlist

* Enable SFTP on switch:
    * HPE Aruba: `ip ssh filetransfer`
    * HP ProCurve `ip ssh` and `ip ssh filetransfer`

* Install git and gitlist:
  `apt-get install git libapache2-mod-php php-xml`
  Enable mod_rewrite in apache
* Set BACKUP_WEB_BASE to the base URL to GitList with repo

# Example repository setup:

## Create backup user:

`adduser config_backup`

Run the following commands to create a repository:

```
mkdir /home/config_backup/Backup
cd /home/config_backup/Backup
git init
```

Add to django settings.py:

```
BACKUP_PATH '/home/config_backup/Backup'
BACKUP_WEB_BASE = 'http://switchinfo.domain.local/gitlist/Backup/blob/master/'
BACKUP_WEB_BASE = '/gitlist/configs/blob/master/'


```

Add to apache site config:

```     
Alias /gitlist /var/www/html/gitlist

<Directory "/var/www/html/gitlist">
    Require all granted
    AllowOverride all
</Directory>
```

# Install GitList 2.0 (Requires PHP 8.1)

## Download

```shell
mkdir /var/www/html/gitlist
cd /var/www/html/gitlist
wget https://github.com/klaussilveira/gitlist/releases/download/2.0.0/gitlist-2.0.0.zip
unzip gitlist-2.0.0.zip
rm gitlist-2.0.0.zip
mkdir -p var/cache
chmod 777 var/cache
mkdir -p var/log
chmod 777 var/log
```

# Install GitList 1.1.1 (PHP older than 8.1)

## Download

````shell
mkdir /var/www/html/gitlist
cd /var/www/html/gitlist
wget https://github.com/klaussilveira/gitlist/releases/download/1.1.1/gitlist-1.1.1.zip
unzip gitlist-1.1.1.zip
rm gitlist-1.1.1.zip
mkdir cache
chmod 777 cache
````

## Configure

```shell
cp config.ini-example config.ini
nano config.ini
```

Change repositories[] to your repository root path (/home/config_backup)

## Configure

nano config/config.yml
`  default_repository_dir: /home/config_backup`

# Enable apache mod_rewrite

````shell
a2enmod rewrite
````
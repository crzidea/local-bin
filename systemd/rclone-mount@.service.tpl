[Unit]
Description=rclone mount for %i
After=network-online.target

[Service]
Type=simple
User=__USER__
Group=__GROUP__
ExecStart=/usr/bin/rclone mount %i:/ /mnt/%i --allow-other --vfs-cache-mode writes
ExecStop=/bin/fusermount -u /mnt/%i
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
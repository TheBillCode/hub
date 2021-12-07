/sbin/ip route|awk '/default/ { print $9 }' > psconfig/app/host_ip

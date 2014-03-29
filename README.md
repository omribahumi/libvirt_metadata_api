Libvirt Metadata API
====================

If you want to use libvirt with cloud-init compatible images, you've come to the right place.  
This project is aimed at implementing EC2 like Metadata API for libvirt.

How does it work
----------------
I'm utilizing the `<metadata>` libvirt domain tag for specifying the instance's metadata.  
The Tornado web server queries the ARP table to find out the source MAC address of the request, then, it queries libvirt for all active domains, checking the MAC addresses of all of them - finding the domain that originated the request.

Example domain XML metadata
---------------------------
```
<domain type="kvm">
    <metadata>
        <instance-id>i-12345678</instance-id>

        <!-- note that the userdata's indentation is safe,
             just indent it as you would normally indent a YAML document.
             see utils/xml.py for more information -->
        <userdata>
            #cloud-config
            disable_root: False
            ssh_pwauth: False
            manage_etc_hosts: False
        </userdata>

        <public-keys>
            <public-key name="my-public-key1">
                <key format="openssh-key">ssh-rsa my-public-key1 foo@bar</key>
            </public-key>
        </public-keys>
    </metadata>
    
    <!-- extra domain data goes here -->
</domain>
```

My setup
--------

This project has been tested on Ubuntu Precise (12.04) with libvirt 1.1.1 from the [CloudArchive Havana repository](https://wiki.ubuntu.com/ServerTeam/CloudArchive).  
I use KVM with QEMU as my virtualization layer with a bridged interface for networking.  
I've tested it with [Precise 64bits Ubuntu cloud images](http://cloud-images.ubuntu.com/precise/current/)
I should mention that I failed building it inside a virtualenv - apparently because `libvirt` 1.1.1 wasn't compiled with LXC support. I didn't have the time to debug this further.  
In the mean time, you can use the `python-libvirt` apt package instead.

After taking care of all the requirements, you can just run it using `./main.py`

Setting up iptables
-------------------

Because we need to "hijack" traffic to the metadata API IP address `169.254.169.254`, we're going to redirect this traffic to `localhost` using IPtables:  
`iptables -t nat -A OUTPUT -d 169.254.169.254 -p tcp --dport 80 --syn -j REDIRECT --to-port 1024`  
Don't forget to persist this iptables rule across reboots with some sort of script (`iptables-persistent` apt package is a good candidate)

Known issues
------------

* NAT network interface is not supported, since you can't tell from which domain (machine) the packet originated

Troubleshooting
---------------
If for some reason you want to troubleshoot why the metadata API doesn't work and you want to query the metadata service on the domain's behalf, you can enable `X-Forwarded-For` and query it using `cURL`:  

```
$ ./main.py --enable-xheaders
```

And in another terminal:

```
$ curl -H 'X-Forwarded-For: 192.168.0.39' http://127.0.0.1:1024/; echo
1.0
2007-01-19
2007-03-01
2007-08-29
2007-10-10
2007-12-15
2008-02-01
2008-09-01
2009-04-04
2011-01-01
2011-05-01
2012-01-12
latest
$ curl -H 'X-Forwarded-For: 192.168.0.39' http://127.0.0.1:1024/latest/; echo
meta-data
user-data
$ curl -H 'X-Forwarded-For: 192.168.0.39' http://127.0.0.1:1024/latest/meta-data/; echo
instance-id
local-ipv4
public-ipv4
public-keys/
$ curl -H 'X-Forwarded-For: 192.168.0.39' http://127.0.0.1:1024/latest/meta-data/instance-id; echo
i-12345678
$ curl -H 'X-Forwarded-For: 192.168.0.39' http://127.0.0.1:1024/latest/meta-data/public-ipv4; echo
192.168.0.39
$ curl -H 'X-Forwarded-For: 192.168.0.39' http://127.0.0.1:1024/latest/meta-data/local-ipv4; echo
192.168.0.39

```

If you get a 500 error, that's probably because the domain's IP address was removed from the arp cache. Simply ping the IP address of the domain to get it back in there.

Fully working domain.xml
------------------------
```
<domain type='kvm'>
  <metadata>
    <instance-id>i-12345678</instance-id>
    <userdata>
      #cloud-config
      disable_root: False
      ssh_pwauth: False
      manage_etc_hosts: False
    </userdata>
    <public-keys>
      <public-key name="admin">
        <key format="openssh-key">ssh-rsa your-ssh-key-goes-here foo@bar</key>
      </public-key>
    </public-keys>
  </metadata>

  <name>test</name>
  <memory>1048576</memory>
  <vcpu>1</vcpu>

  <os>
    <type>hvm</type>
    <boot dev='hd' />
  </os>

  <features>
    <acpi />
  </features>

  <clock offset='utc' />

  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>

  <devices>
    <emulator>/usr/bin/qemu-system-x86_64</emulator>

    <serial type='pty'>
      <target port='0' />
    </serial>

    <console type='pty'>
      <target type='serial' port='0' />
    </console>

    <interface type='bridge'>
      <source bridge='br0' />
    </interface>

    <input type='mouse' bus='ps2' />
    <graphics type='vnc' port='5001' listen='0.0.0.0' />

    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' cache='none' />
      <source file='/home/omrib/kvm/precise-server-cloudimg-amd64-disk1.img' />
      <target dev='vda' bus='virtio' />
      <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0' />
    </disk>
  </devices>
</domain>
```
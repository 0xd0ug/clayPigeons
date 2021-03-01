# clayPigeons

### Overview

ClayPigeons is a simple program I wrote to help me with my service detection research. It parses nmap's `nmap-service-probes` file and starts sub-processes with listening sockets that respond in such a way that, if you run an nmap scan against the server, nmap should respond as if various random services are running on the system.

Start clayPigeons from the Linux command line as `python3 clayPigeons.py`. Use CTRL-C to exit.

ClayPigeons now attempts to locate the `nmap-service-probes` file in its own directory, then in common locations and finally using the OS command locate. It will throw an exception if it can't find the file. Also, ClayPigeons saves its configuration in a file `cp.conf`. If you run ClayPigeons a second time with this file in the directory, it will load the configuration from that file. This will allow you to replay experiments. Deleting the `cp.conf` file will cause clayPigeons to create a new random configuration.

A new experimental feature has been added that lets the user have some control over which services are chosen. By adding strings to the `onlyMatch` variable, clayPigeons will only load matches that contain the strings specified. So, for example, adding "http" to that list will only add probes with the word "http" in their lines. Changing this and then using an old config file, or specifying a filter for which there are too few matches can cause the program to fail.
### Prerequisites

ClayPigeons was developed to run on a Mac or Linux system. It uses Python3 and requires the exrex library, as well as a current installation of nmap. You'll need to edit the path to nmap-service-probes in the source code to point to wherever that file is on your system.

### Disclaimers

I created this for educational purposes only, specifically to help me conduct research towards my dissertation. While I took precautions (localhost listening only by default, safer eval functions, etc.), running this on any production system is a really bad idea.

I have no affiliation with nmap other than being a really big fan. This tool requires a file from nmap, and the best way to get that file is to install nmap itself.

This program is a work in progress, in the early development stages, and will be modified to adapt to my research. I only made this repo public because a colleague saw the output and wanted to use it. It does not properly emulate all services, has confusing debugging-style output, and may have other issues as well. :-) Use at your own risk!

### Limitations

A new Python process is created for each listener. There must be a better way to do this, but it works fine for me right now.

Exrex doesn't handle all the regular expressions and will occasionally print an error message beginning with `[!] cannot handle expression`.

SSL services are not yet implemented.

The list of limitations in the README file is incomplete.

### Sample Output

Below is an excerpt from sample output of an nmap scan run on a Kali Linux box with clayPigeons:

````# nmap 127.0.0.1 -p- -sV
Starting Nmap 7.91 ( https://nmap.org ) at 2020-12-19 12:54 EST
Nmap scan report for localhost (127.0.0.1)
Host is up (0.000015s latency).
Not shown: 65490 closed ports
PORT      STATE SERVICE            VERSION
390/tcp   open  ldap
548/tcp   open  afp                Netatalk _._- (name: MyBookWorld; protocol 3.3)
554/tcp   open  am-pdp             amavisd-new AM.PDP 2.4.5
706/tcp   open  silc               SILCd conferencing service
992/tcp   open  telnets?
994/tcp   open  ssl/ircs?
1080/tcp  open  socks4             (Connection rejected or failed; connections possibly ok)
1111/tcp  open  smtp               qmail smtpd
1433/tcp  open  ms-sql-s           Microsoft SQL Server 2008 10.00.6241; SP4+ MS15-058
1501/tcp  open  crossmatchverifier Cross Match Verifier E fingerprint advanced control (Gain: 2464351395; Contrast: 5854711829479; Time: 52285453; Illumination: 646523866567390)
1521/tcp  open  oracle?
1583/tcp  open  psql-btrieve       Pervasive.SQL Server - Btrieve Engine
1720/tcp  open  lineage-ii         L2J Lineage II game server
1883/tcp  open  mqtt
2181/tcp  open  zookeeper          Zookeeper .--.-.. (Built on //./.)
3310/tcp  open  dyna-access?
3333/tcp  open  kumo-manager       Kumofs
3388/tcp  open  ms-wbt-server      Microsoft Terminal Services
3389/tcp  open  ms-wbt-server      Microsoft Terminal Services
4369/tcp  open  epmd               Erlang Port Mapper Daemon
4533/tcp  open  rotctld            Hamlib rotctld (model: $]i5hsFu8(F`a:e6s)
4567/tcp  open  tram?
5555/tcp  open  adb                Android Debug Bridge (token auth required)
5800/tcp  open  http               APC SmartUPS http config
6050/tcp  open  minecraft          Minecraft game server
6715/tcp  open  jmon               JMON for zOS (FMID HALG300)
6996/tcp  open  java-rmi           Java RMI
8008/tcp  open  ajp13              Apache Jserv (Protocol v1.3)
8081/tcp  open  http-proxy-ctrl    WWWOFFLE proxy control (Unauthorized)
8728/tcp  open  lotusnotes         Lotus Domino server (CN=-..-- .  - -;OU= ...  ..-   -. /.. ..... . - ;Org=---- - .)
9095/tcp  open  oo-defrag          O&O Defrag
9096/tcp  open  oo-defrag          O&O Defrag
9098/tcp  open  drda?                                                                                                                                    
9099/tcp  open  drda                                                                                                                                     
10000/tcp open  rtsp               Helix Mobile Server rtspd _.-...-.-                                                                                   
10310/tcp open  tcpwrapped                                                                                                                               
10333/tcp open  teamtalk           BearWare TeamTalk (protocol: 2.0.4434755.0360)                                                                        
10512/tcp open  tcpwrapped
10601/tcp open  unknown
14238/tcp open  unknown
19700/tcp open  rhpp               Ricoh Reliability Host Printing Protocol
25565/tcp open  minecraft?
41523/tcp open  wow                World of Warcraft authserver (realm: I;FSU>m@ko&J n+MFW on 54756.2303:33462892)
60022/tcp open  ibm-db2            IBM DB2 Database Server```

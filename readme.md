### Run tests
`python -m unittest` (from the repository root)

### Set up and run full masternode

Cloud instance (or bare metal server) is required. Minimal recommended instance configuration:

 - Ubuntu 18.04 LTS
 - 2 GB RAM
 - 2 CPU
 - 50 GB of free space (as blockchain data will grow)
 - The following ports should be opened from the outside (in AWS it is done by security groups)
  - - 4444
  - - 19932
  - - 19933
  - - 9932
  - - 9933

Recommended instance setup:

 - Create user animecoinuser: `adduser animecoinuser`. Set up a password, leave all fields empty and answer Y at the end.
 - Add sudo ability for the user: `usermod -aG sudo animecoinuser`
 - Allow user perform `sudo` operations without password: `sudo visudo`, then add `animecoinuser ALL=(ALL:ALL) ALL` into `# User privilege specification` section.

##### PastelD installation
    Building PastelD from sources is out of scope for this documentation.
    Please refer to https://github.com/PastelNetwork/Pastel for this.
    This guide uses precompiled binaries.

 - Log in into instance under `animecoinuser` user
 - Download pasteld binaries: `wget dobrushskiy.name/static/pastel.tar.gz`
 - Unpack it: `tar -xzvf pastel.tar.gz`
 - Install dependency: `sudo apt-get update && sudo apt-get install -y libgomp1`
 - Fetch some blockchain parameters `./fetch-params.sh` (it may take a while)

 Then create configuration for pasteld:

 - `mkdir ~/.pastel/`
 - `touch ~/.pastel/pastel.conf`
 - `printf "testnet=1\nserver=1\naddnode=18.224.16.128\nrpcuser=rt\nrpcpassword=rt\nrpcallowip=0.0.0.0/0\n" > ~/.pastel/pastel.conf`

 Run blockchain daemon

 - `./pasteld &`

##### Python masternode installation

 - Get source code: `wget dobrushskiy.name/static/StoVaCore.tar.gz`
 - Unpack: `tar -xzvf StoVaCore.tar.gz`
 - `cd StoVaCore`
 - `./install_pynode.sh` - this will install dependencies

Generate certificate for python masternode https

 - `mkdir /home/animecoinuser/.pastel/pynode_https_cert`
 - `cd /home/animecoinuser/.pastel/pynode_https_cert`
 - `openssl req -newkey rsa:2048 -nodes -keyout privkey.pem -x509 -days 36500 -out certificate.pem -subj "/C=US"`

 - Install SQLite 3.25+ (described in section below)
 
 Run python masternode:
 - `python3 start_single_masternode.py &`

###### Additinal dependencies
 
  - SQLite version 3.25 or higher (for window function support). Currently Ubuntu 18.40 repositories has only SQLite 3.22.
  Replace SQLite .SO:
   - download sources:
    wget https://www.sqlite.org/2020/sqlite-autoconf-3310100.tar.gz
    - unpack, build (./configure, make)
    - ..or download built for ubuntu 18.04 `wget https://dobrushskiy.name/static/libsqlite3.so.0` - it's much faster then building.
    - backup original
    sudo mv /usr/lib/x86_64-linux-gnu/libsqlite3.so.0 /usr/lib/x86_64-linux-gnu/libsqlite3.so.0.original
    - put new version
    sudo cp libsqlite3.so.0 /usr/lib/x86_64-linux-gnu/
  
  
### Install and run pyNode (Ubuntu 18.04)

 - `pasteld` should be started and running
 - python3.6 should be installed
 - `apt install python3-pip`
 - `pip3 install -r requirements.txt`
 - `python start_single_masternode.py &`
 - pyNode is running, listening connections on port 4444

### Tools/scripts
 - `python test_rpc.py` - connects to pyNodes from local `masternodes.conf` file, send ping packet with zeroMQ RPC. If any node hangs with response - it probably requires restart.

# HTTPrint

A very simple web interface to upload and print files.


## Install and run

To install it:
``` bash
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
# if you want to install these modules for an unprivileged user, add --user and remove "sudo";
# if you want to upgrade the versions already present in the system, also add --upgrade
sudo pip3 install tornado
git clone https://github.com/alberanid/httprint
cd httprint
./httprint.py --debug
```

Now you can **point your browser to [http://localhost:7777/](http://localhost:7777/)**

You can also **run the server in https**, putting in the *ssl* directory two files named *httprint_key.pem* and *httprint_cert.pem*

By default the **--print-with-code** argument is true, and the uploaded files are just scheduled for priting. To actually print them, you should supply the generated code, for example: `curl -X POST http://localhost:7777/api/print/1234`


# License and copyright

Copyright 2019 Davide Alberani <da@mimante.net>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


# Manager
Manager is a bundle of scripts written in Python to manage a production 
server easier.

## Server configuration
Manager assume that you already have on your server Docker installed on
an Ubuntu 16.04 LTS at least.

### Setup
For the first run, you must setup basic containers on your server. It 
includes NGinx to handle HTTP requests and PostgreSQL to store databases.

By default, Manager add an instance of Portainer to your server but does
not start it.

To setup, run:
```
sudo manager setup <server domain>
```

The server domain is the default server domain which would be given to
NGinx and used for the Portainer container.

#### Security consideration
We recommand you to restrict trafic to any port different than 80 or 443
to your server. To achieve that, use UFW.

### Deploy an application
Manager assume each application needs to run a container and a postgres
database.

```
sudo manager deploy <image> <appname> <domain>
```

**Note**: When an app is deployed, an environment file is created into 
`/var/conf/environements` and contains, at least, the DATABASE_URL.

### Refresh an app
```
sudo manager redeploy <appname> [-f]
```

**Note**: If you want to force refresh add `-f` option after the 
application name.

## Licence

[![GNU GPL v3.0](http://www.gnu.org/graphics/gplv3-127x51.png)](http://www.gnu.org/licenses/gpl.html)

```
Manager - Easier server management
Copyright (C) 2017 Philippe VIENNE
Copyright (C) 2017 BdE INSA Lyon

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
```
#!/bin/sh

# This script tries to install an LCFIT instance on the local system.
# This script expects to be run from the downloaded source tree for
# LCFIT, otherwise it won't know where to find files to install
# locally.

# Note:  Predefine and assume usernames "lcfit" and "lcfit_test".

# Note: Separate install from db backup.  I hope to be able to do in
# two steps: install an instance with this script, then install a
# dumped database from a db backup into that instance, and have
# everything work.

# Hehe: echo {1..10} | sed 's% %/%g' -> 1/2/3/4/5/6/7/8

#### Environment variables for installation ####################
export APACHE_CONFIG_ROOT='/etc/apache2' # where do we find the apache config files?
export APACHE_CONFIG_FILE="$APACHE_CONFIG_ROOT/httpd.conf"	# What is the main apache config file?
export MODPYTHON_CONFIG_FILE="$APACHE_CONFIG_ROOT/modules/16_mod_python.conf" # what is the mod_python config file?

export APACHE_HTDOCS_ROOT='/var/www/localhost/htdocs' # Where the main htdocs goes
export LCFIT_APP_ROOT="$APACHE_HTDOCS_ROOT/larry" # Where do we put the main code to be run?
export LCFIT_SOURCE_ROOT=`echo $PWD | sed 's%/[^/]*/[^/]*$%%' `  # Root of source (up two dirs up from cwd).
export LCFIT_WWW_ROOT="/larry/lc" # What is the URL path for the LCFIT thing when running under apache?

export LCFIT_DATABASE="larrydb" # What do we call the main database (Do we need a db user for postgres?)
#### End Envars ################################################

##### httpd conf file ##########################################

# Create lcfit.httpd.conf with template.  Get correct paths by subbing
# in ENVAR values from above....  
cheetah compile lcfit.httpd.conf.tmpl
python ./lcfit.httpd.conf.py --env --stdout > lcfit.httpd.conf

# ... install the apache config addition in the apache root ...
cp --backup=numbered lcfit.httpd.conf "$APACHE_CONFIG_ROOT"

# ... grep the apache config file for a likely include, then if necessary,
# add the line at the end...
if grep "#LCFIT" "$APACHE_CONFIG_FILE" 1>/dev/null ; then 
	echo "Line containing \"#LCFIT\" already in $APACHE_CONFIG_FILE.  Not doing anything."
else
	echo >> "$APACHE_CONFIG_FILE"
	echo "#LCFIT configuration settings include:" >> "$APACHE_CONFIG_FILE"
	echo "Include $APACHE_CONFIG_ROOT/lcfit.httpd.conf" >> "$APACHE_CONFIG_FILE"
	echo >> "APACHE_CONFIG_FILE"
fi

# ... update httpd authentication.  Finis.
htpasswd -b "$APACHE_CONFIG_ROOT/lcfit.htpasswd" lcfit password
htpasswd -b "$APACHE_CONFIG_ROOT/lcfit.htpasswd" lcfit_test password

#### End httpd configuration ############################################

##### modpython configuration ###########################################
# Create modpython config file with ENVARS
cheetah compile ./lcfit.modpython.conf.tmpl
python ./lcfit.modpython.conf.py --env --stdout > lcfit.modpython.conf

# Install the modpython config in apache root
cp --backup=numbered lcfit.modpython.conf "$APACHE_CONFIG_ROOT/lcfit.modpython.conf"

# Add Include line in "containing" modpython file
if grep "#LCFIT" "$MODPYTHON_CONFIG_FILE" 1>/dev/null ; then 
	echo "Line containing \"#LCFIT\" already in $MODPYTHON_CONFIG_FILE.  Not doing anything."
else
	echo >> "$MODPYTHON_CONFIG_FILE"
	echo "#LCFIT configuration settings include:" >> "$MODPYTHON_CONFIG_FILE"
	echo "Include $APACHE_CONFIG_ROOT/lcfit.modpython.conf" >> "$MODPYTHON_CONFIG_FILE"
	echo >> "$MODPYTHON_CONFIG_FILE"
fi

#### End modpython configuration #######################################

#### cron scripts ###################################################
#Output cron lines with script locations for insertion into the LCFIT
#admin's crontab.
echo
echo "Add the following lines to your crontab"
echo "2 1 * * * /usr/bin/python $LC_SOURCE_ROOT/MAINTENANCE/daily.py"
echo "3 2 * * 7 /usr/bin/python $LC_SOURCE_ROOT/MAINTENANCE/weekly.py"
echo 

#### Database ################################################################
psql "$LCFIT_DATABASE" -f "larrydb.sql"

#### Application ################################################################
cp -pri "$LCFIT_SOURCE_ROOT/PYTHON_VERSION/" "$LCFIT_APP_ROOT"
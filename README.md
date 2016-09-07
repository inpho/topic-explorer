# InPhO Topic Explorer

[![Join the chat at https://gitter.im/inpho/topic-explorer](https://badges.gitter.im/inpho/topic-explorer.svg)](https://gitter.im/inpho/topic-explorer?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Travis](https://img.shields.io/travis/inpho/topic-explorer.svg)](https://travis-ci.org/inpho/topic-explorer)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/inpho/topic-explorer/blob/master/LICENSE.txt)
[![PyPI](https://img.shields.io/pypi/v/topicexplorer.svg)](https://pypi.python.org/pypi/topicexplorer)

This interactive visualization displays information from the LDA topic models generated using the [InPhO VSM module](http://github.com/inpho/vsm/). Live demos trained on the Stanford Encyclopedia of Philosophy, a selection of books from the HathiTrust Digital Library, and the original LDA training set of Associated Press articles are available at [http://inphodata.cogs.indiana.edu](http://inphodata.cogs.indiana.edu/).

The color bands within each article's row show the topic distribution within that article, and the relative sizes of each band indicates the weight of that topic in the article. The total width of each row indicates similarity to the focal topic or document, measured by the quantity sim(doc) = 1 – JSD(doc, focus entity), where JSD is the Jensen-Shannon distance between the word probability distributions of each item. Each topic's label and color is arbitrarily assigned, but is consistent across articles in the browser.

Display options include topic normalization, alphabetical sort and topic sort. By normalizing topics, the combined width of each bar expands so that topic weights per document can be compared. By clicking a topic, the documents will reorder acoording to that topic's weight and topic bars will reorder according to the topic weights in the highest weighted document. When a topic is selected, clicking "Top Documents for [Topic]" will take you to a new page showing the most similar documents to that topic's word distribution. The original sort order can be restored with the "Reset Topic Sort" button.

## Installation
There are two types of install: Default and Developer.

### Default Install
1.  Install the [Anaconda Python 2.7 Distribution](http://continuum.io/downloads).
2.  Open a Terminal (Mac and Linux) or PowerShell (Windows).
3.  Run `pip install --pre topicexplorer -i https://inpho.cogs.indiana.edu/pypi/`.
    
    **Note:** `--pre` has *two* `-` characters. When the `1.0` release happens, `--pre` will no longer be necessary.
4.  Test installation by typing `topicexplorer -h` to print usage instructions.

### Developer Install
1.  [Set up Git](https://help.github.com/articles/set-up-git/)
2.  Install the [Anaconda Python 2.7 Distribution](http://continuum.io/downloads).
3.  Open a terminal and run `pip install --src . -e git+https://github.com/inpho/topic-explorer#egg=topicexplorer`
4.  Test installation by typing `topicexplorer -h` to print usage instructions.

## Usage
![Workflow](http://inphodata.cogs.indiana.edu/img/workflow.png)

1.  Initialize the Topic Explorer on a file, folder of text files, or folder of folders:

    ```
    topicexplorer init PATH [CONFIG]
    ```

    This will generate a configuration file called *CONFIG*.

2.  Train LDA models using the on-screen instructions:

    ```
    topicexplorer train CONFIG
    ```

3.  Launch the topic explorer:

    ```
    topicexplorer launch CONFIG
    ```

4.  Press Ctrl+C to quit all servers.

See the sample configuration files in the `config` directory for examples of how to extend the topic explorer.

## Bug Reports
Please report issues on the [issue tracker](http://github.com/inpho/topic-explorer/issues) or contact Jaimie directly (contact info at bottom of README).

In your report, please include the error message, the command you ran, your operating system, and the output of the command `topicexplorer version`. This will ensure that we can quickly diagnose your issue.

**Note:** When using a developer install `topicexplorer version` will print in the following format: `1.0b39-1-g7c834bf-dirty`.
* The first part is the most recent release tag. (`1.0b39`)
* The second part is the number of commits since the tag. (`1`)
* The next is the hash of the most recent commit. (`g7c834bf`)
* The optional `-dirty` flag indicates that the local repository has uncommitted changes.

## Alternate Installs
We highly recommend using the Anaconda Python 2.7 Distribution. Straightforward instructions are provided above for Anaconda Python 2.7 for both end users and developers. Both of these installs are officially supported.

Below we offer guidance for installing side-by-side with an Anaconda Python 3.5 install or for installing it without Anaconda, with notes on dependencies.

### Python 3 Install
The InPhO Topic Explorer is **only** compatible with Python 2.7. However, Anaconda for Python 3.5 makes it easy to set up a side-by-side install of Python 2.7 so you can use both Python 3.5 and Python 2.7.

1.  Install the [Anaconda Python 3.5 Distribution](http://continuum.io/downloads).
2.  Open a terminal and run `conda create -n py27 python=2.7 anaconda`. This will create a Python 2.7 Anaconda environment.
3.  Run `source activate py27` to activate the Python 2.7 bindings. You should see `(py27)` before your prompt.
4.  Use either the Default or Developer [install instructions](#installation), skipping the step to install Anaconda Python 2.7.
5.  Run `source deactivate` to deactivate Python 2.7 bindings and reactivate Python 3.5 bindings. Note that the `topicexplorer` command will only work when the Python 2.7 bindings are activated.

### Non-Anaconda Install
 - **Miniconda**
   1.  If using Miniconda (a small version of Anaconda), the necessary packages are: `conda install numpy scipy nltk matplotplib ipython networkx`

 - **Debian/Ubuntu**
   1.  `sudo apt-get-install build-essential python-dev python-pip python-numpy python-matplotlib python-scipy python-ipython`

   2.  [IPython Notebooks](http://ipython.org/install.html)

 - **Windows**
   1.  Install [Microsoft Visual C++ Compiler for Python 2.7](http://www.microsoft.com/en-us/download/details.aspx?id=44266)

   2.  Install the Python packages below:
       *   [Numpy](http://sourceforge.net/projects/numpy/files/NumPy/)
       *   [Scipy](http://sourceforge.net/projects/scipy/files/scipy/)
       *   [matplotlib](http://matplotlib.org/downloads.html)
       *   [IPython Notebooks](http://ipython.org/install.html)

## Deployment
The Topic Explorer includes a simple HTTP server through the Bottle Web Framework. This simple server is what the `topicexplorer launch` and `topicexplorer serve` commands use.

If you wish to host a high-traffic version of InPhO-TE, we recommend using the Apache Web Server and the mod_wsgi module. This infrastructure powers the demos at [http://inphodata.cogs.indiana.edu/] and is readily available on cloud compute platforms. Details for that configuration are below.

If you have deployed InPhO-TE using another infrastructure, please submit a pull request with the documentation. The function `topicexplorer.server.create_app` will make a WSGI-compliant application for use with any WSGI-compliant server.

### mod_wsgi

1.  Install apache2 with mod_wsgi: `apt-get install apache2 libapache2-mod-wsgi`
2.  Create `/etc/apache2/sites-available/topicexplorer.conf`:
    ```
<VirtualHost *:80>
	ServerName localhost
	ServerAdmin admin@localhost
	
	ErrorLog /var/www/topicexplorer/log/error.log
	CustomLog /var/www/topicexplorer/log/access.log combined

	WSGIDaemonProcess topicexplorer user=www-data group=www-data \
	  python-path=/home/jaimie/anaconda2/lib/python2.7/site-packages/
	WSGIScriptAlias /ap /var/www/topicexplorer/app.wsgi
	
	<Directory /var/www/topicexplorer>
		WSGIProcessGroup topicexplorer
		WSGIApplicationGroup %{GLOBAL}
		Options All
		AllowOverride All
		Require all granted
	</Directory>
</VirtualHost>
```
3.  Create the application directory: `sudo mkdir -p /var/www/topicexplorer/`
4.  Create the log directory: `sudo mkdir -p /var/www/topicexplorer/log`
5.  Create the www directory: `sudo mkdir -p /var/www/topicexplorer/www`
6.  Create the config directory: `sudo mkdir -p /var/www/topicexplorer/config`
7.  Add a symlink from `/var/www/topicexplorer/` to `app.wsgi`. For example: `ln -s /home/jaimie/workspace/topic-explorer/app.wsgi /var/www/topicexplorer/app.wsgi`
8.  Add a symlink to your `.ini` files in the `/var/www/topicexplorer/config` directory. For example, if working with the AP corpus trained in my home directory: `ln -s /home/jaimie/ap.ini /var/www/topicexplorer/config/ap.ini`
9.  Enable the site: `sudo a2ensite topicexplorer`
10.  Restart apache: `sudo apache2ctl restart`
11.  Test the site at [http://localhost/]. If an HTTP 500 Internal Server Error is returned, check the log in `/var/www/topicexplorer/log/error.log`.


#### Caching
Credit to [Digital Ocean](https://www.digitalocean.com/community/tutorials/how-to-configure-apache-content-caching-on-ubuntu-14-04) for a very helpful guide.

To enable caching:
1.  Modify `/etc/apache2/sites-available/topicexplorer.conf` to add Cache directives before the closing `</VirtualHost>` tag:
```
<VirtualHost *:80>
    # ...

	CacheQuickHandler off

	CacheLock on
	CacheLockPath /tmp/mod_cache-lock
	CacheLockMaxAge 5

	CacheIgnoreHeaders Set-Cookie

	<Location />
		CacheEnable disk
		CacheHeader on

		CacheDefaultExpire 600
		CacheMaxExpire 86400
		CacheLastModifiedFactor 0.5
	</Location>
</VirtualHost>
```
2.  Enable caching modules: `sudo a2enmod cache && sudo a2enmod cache_disk`
3.  Restart apache: `sudo apache2ctl restart`


#### Server Status
The following snippet may help debug issues, enabling you to visit [http://localhost/server-status] to find more details. Remove these lines for production environments.
```
<VirtualHost *:80>
    # ...

	<Location /server-status>
		SetHandler server-status
		
		Order Deny,Allow
		Allow from all
	</Location>
</VirtualHost>
```

## Licensing and Attribution
The project is released under an [Open-Source Initiative-approved MIT License](http://opensource.org/licenses/MIT).

The InPhO Topic Explorer may be cited as:

 -  Jaimie Murdock and Colin Allen. (2015) *Visualization Techniques for Topic Model Checking* in Proceedings of the 29th AAAI Conference on Artificial Intelligence (AAAI-15). Austin, Texas, USA, January 25-29, 2015. [http://inphodata.cogs.indiana.edu/](http://inphodata.cogs.indiana.edu/)

A [BibTeX file](https://github.com/inpho/topic-explorer/blob/master/citation.bib) is included in the repository for easier attribution.

## Collaboration and Maintenance
The InPhO Topic Explorer is maintained by [Jaimie Murdock](http://jamram.net/):

 -  E-mail: jammurdo@indiana.edu
 -  Twitter: [@JaimieMurdock](http://twitter.com/JaimieMurdock)
 -  GitHub: [@JaimieMurdock](http://github.com/JaimieMurdock)
 -  Homepage: [http://jamram.net/](http://jamram.net/)

Please report issues on the [issue tracker](http://github.com/inpho/topic-explorer/issues) or contact Jaimie directly.

We are open to collaboration! If there's a feature you'd like to see implemented, please contact us and we can lend advice and technical assistance.

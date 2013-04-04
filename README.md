overblock
=========

###Description

A web application focused on being run locally, that functions somewhat like blockexplorer, and operates on bitcoind.

###Features

* Last *k* recently mined blocks
* Block view, by blockhash, or by block height
* Transaction view
* Raw block/transaction view

###Lib Requirements

* [PyYaml](http://pyyaml.org/)
* Inlcudes Jeff Garzik's [python-bitcoinrpc](https://github.com/jgarzik/python-bitcoinrpc) project which is under the LGPL. See files for individual licence.
* Includes `servlet.py`, which is written by Stephen "Zero" Chappell <Noctis.Skytower@gmail.com>, and was released under the MIT license; see file for details.

The rest of the project is released under the MIT license, unless otherwise noted.






###Instructions

* Make sure to run bitcoind with `tindex=1`, either on the command line as `-tindex=1` or in the `bitcoin.conf` file as `tindex=1`. If you did not do this at first, it may require you to run `bitcoind` once with -reindex.
* Copy `config.yml.default` to `config.yml`, edit the configuration as necessary.
* `blk_get_txs` means that when requesting block information, the application will also retreive the transaction information for the block. If this option is set, then the fields that depend on the transaction information will be displayed.
* `blk_get_tx_inputs` means that when iterating through each transaction, the application will follow the input transactions back to their source output transactions and display this information when useful/necessary.
* `listen_port`, an integer denoting the port for the web application interface to listen on.

###Usage

* Run `python main.py`.
* Using a web-browser, browse to `http://localhost:<listen_port>/`, where `<listen_port>` is the port indicated in your configuration.




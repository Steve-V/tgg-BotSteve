Part of BotSteve is the Automagic Storage Framework. For modules that opt in, the bot manages a key/value store.

How to Use
----------
If you are writing a module and would like a managed datastore, just set a `storage` attribute in your module like this:

```python
storage = {}
```

The bot will then populate this with the stored values.

### Default Values ###
If you would like to have default values in your store, simply put them in the `storage` attribute in your module:

```python
storage = {
	'spam': 'eggs',
	'spamspam': 'spam',
	}
```

The bot will use this when creating your datastore.

### Other Considerations ###
To simplify the job of the datastore backend, please keep to the following rules:

* Keys are strings.
* Values are JSON-able objects. That is, it maybe be a bool, number, string, list/tuple, or dict containing the same.
* If a callback accesses the datastore, it should be threaded (the default).

Technical Details
-----------------
On load and registration, Phenny checks to see if the module has a `storage` attribute. If it does, it loads a datastore for the module and places it in `storage`.

If Phenny must create a store, it is populated with the value of `storage`.

The object saved to `storage` implements the `MutableMapping` interface, as defined by `collections.MutableMapping`.

Methods on `storage` are all syncronous. If IO must happen (eg, to a database server), it will block.

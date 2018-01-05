# Hash JupyterHub Authenticator

An authenticator for [JupyterHub](https://jupyterhub.readthedocs.io/en/latest/) where the password for each user is a secure hash of its username. Useful for environments where it's not suitable for users to authenticate with their Google/GitHub/etc. accounts.

## Installation

```bash
pip install jupyterhub-hashauthenticator
```

Should install it. It has no additional dependencies beyond JupyterHub.

You can then use this as your authenticator by adding the following lines to your `jupyterhub_config.py`:

```python
c.JupyterHub.authenticator_class = 'hashauthenticator.HashAuthenticator
c.HashAuthenticator.secret_key = 'my secret key'  # Defaults to ''
c.HashAuthenticator.password_length = 10          # Defaults to 6
```

You can generate a good secret key with:
```bash
$ openssl rand -hex 32
0fafb0682a493485ed4e764d92abab1199d73246477c5daac7e0371ba541dd66
```

## Generating the password

This package comes with a command called `hashauthpw`. Example usage:

```bash
$ hashauthpw
usage: hashauthpw [-h] [--length LENGTH] username [secret_key]

$ hashauthpw pminkov my_key
939fd4
```

## JupyterHub service

This package also provides a JupyterHub service which gives administrators a CSV containing all users and their passwords.  This can be used to generate login information for a group of users or to remind a user of their password.  In addition to JupyterHub, this service requires the *requests* package.

It can be enabled through your `jupyterhub_config.py` file:

```python
c.JupyterHub.services = [
  {
    'name': 'hashauth',  # Service will be available at /services/hashauth
    'admin': True,
    'url': 'http://127.0.0.1:10101',  # Pick any free port
    'command': ['hashauthservice', 'jupyterhub-config.py'],  # Second arg is path
  }                                                          # to this file
]
```

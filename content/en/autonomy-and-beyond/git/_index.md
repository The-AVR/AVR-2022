---
title: "Git"
weight: 3
---

In writing software for your drone, you will both need to interact with the sandbox environment as well as collaborate with your peers working on code from different machines. "Git" is built for tracking and managing changes between files. It is a staple of modern code management.

## Windows Install

To install Git, simply select the standalone installer from the [git-scm website](https://git-scm.com/download/win)

Run through the installation process. Once the install is completed, you will need to setup a username and email address for your machine.

## Jetson Install

Git is already installed on your Jetson.

## Git Configuration

Git needs to know who you are.
To set up a username and email address, open a terminal and type the following:

```bash
git config --global user.name "yourusername"
git config --global user.email "email@youremail.com"
```

Remember this email, because you will need to add it to your GitHub account later.

# Online Challenges Plugin for CTFd

> It's a plugin  that uses to generate dynamic flag for `Web` or `Pwn` online envirenment Chanls with dockerfile

## Usage

1. New a Online Challenges with a random token.
2. Copy the token into [send.py](demo/send.py) and change the platfrom url.
3. Copy the `send.py` into your Online envirenment and run it.

* Dockerfile [demo](demo/README.md)

## Install

**Requires**: [CTFd >= 1.1.2](https://github.com/CTFd/CTFd/releases/tag/1.1.2)
> Don't test on earlier version 

* Clone this repository to `CTFd/plugins`

**Notes**: make sure this folder is named `OnlineChallenge` so that `CTFd` can load the assets.

## TODO

- [x] Useage demo
- [ ] Regenerate the flag when it accessed
- [ ] More detailed log file in Serve and Client
- [ ] Optimize Web UI
- [ ] Create and Update the token easier

## [CHANGELOG](CHANGELOG.md)

## Reference

* https://github.com/CTFd/CTFd/wiki/Plugins
* https://mozilla.github.io/nunjucks/cn/templating.html#part-9d9c663eba1f6097


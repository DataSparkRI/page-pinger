# Page Pinger


### Getting Set up
Install requirements.txt

You'll need to create some configuration files, ```urls.conf``` and ```email.conf```. Examples are included

### Usage
```
python ping.py -t 10

```
```-t``` is time in seconds between each ping cycle.


### Requirements
This is written to be run under [supervisord| http://supervisord.org/]

Here is an example supervisor conf

```
[supervisord]
logfile=supervisord.log
loglevel=debug

[program:pinger]
command=python ping.py -t 10
```




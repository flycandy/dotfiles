"""
Usage:
  changehost.py <name>

"""
import docopt
import psutil

fmt = """
127.0.1.1	{name}.qbtrade.org  {name}
127.0.0.1 localhost

{ip}  {name}

"""
args = docopt.docopt(__doc__)
ip = psutil.net_if_addrs()['eth0'][0].address
fmt = fmt.format(ip=ip, name=args['<name>'])
print(fmt)
open('/etc/hosts', 'w').write(fmt)
open('/etc/hostname', 'w').write(args['<name>'] + '\n')

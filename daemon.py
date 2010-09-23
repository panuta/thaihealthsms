#Author:orcun avsar <orc.avs@gmail.com>

import sys, os, time, atexit
from signal import SIGTERM 
 
class Daemon:
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
    
    def daemonize(self):
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit first parent
                sys.exit(0) 
        except OSError, e: 
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
    
        # decouple from parent environment
        os.chdir("/") 
        os.setsid() 
        os.umask(0) 
    
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit from second parent
                sys.exit(0) 
        except OSError, e: 
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1) 
    
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
    
        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)
    
    def delpid(self):
        os.remove(self.pidfile)
 
    def start(self):
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
    
        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        
        # Start the daemon
        self.daemonize()
        self.run()
 
    def stop(self):

        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
    
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart
 
        # Try killing the daemon process    
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)
 
    def restart(self):
        self.stop()
        self.start()
 
    def run(self):
        pass

import datetime
import imp
import settings
import django
from django.core.management import setup_environ

DIR=os.path.abspath(__file__)
sys.path.append(imp.find_module("django")[1])
sys.path.append(os.path.split(os.path.split(DIR)[0])[0])
setup_environ(settings)


class ComponentError(Exception):
    def __init__(self,component,components):
        self.components=components
        self.component=component
    def __str__(self):
        return "Invalid component:"+self.component+". Available components: "+",".join(self.components)
        

class BaseCron(Daemon):
    def __init__(self, pid):
        Daemon.__init__(self, pid)
        self.events={}
        self.components=["year","month","day","hour","minute","second"]

    def add_event(self,event,period,component,round=False):
        if not self.components.count(component):
            raise ComponentError(component,self.components)
        self.events[event]={"period":period,"component":component,"round":round}
        self.find_next(event)

    def find_next(self,event):
        now=datetime.datetime.now()
        comps={"year":now.year,
            "month":now.month,
            "day":now.day,
            "hour":now.hour,
            "minute":now.minute,
            "second":now.second}
        component=self.events[event]["component"]
        period=self.events[event]["period"]
        if component=="year":
            comps[component]+=period
        elif component=="month":
            comps[component]=range(1, 13)[(now.month+period-1)%12]
            if comps[component]==1:comps["year"]+=1
        else:
            karg={component+"s":period} 
            time_delta=datetime.timedelta(**karg)
            next=now+time_delta
            comps={"year":next.year,
                    "month":next.month,
                    "day":next.day,
                    "hour":next.hour,
                    "minute":next.minute,
                    "second":next.second}
        round=self.events[event]["round"]
        if round:
            for comp in self.components[self.components.index(component)+1:]:
                comps[comp]=1
        next_visit=datetime.datetime(**comps)
        self.events[event]["next_visit"]=next_visit

    def run(self):
        while 1:
            ###sorting job###
            list=[(self.events[x]["next_visit"],x) for x in self.events.keys()]
            list.sort()
            event_name=list[0][1]
            event_date=list[0][0]
            now=datetime.datetime.now()
            timedelta=event_date-now     
            seconds=(timedelta.days*24*60*60)+timedelta.seconds
            print "\nnext job: '"+event_name +"' after:", str(timedelta)
            if timedelta.days>=0:
                while seconds:
                    if seconds>1000:
                        time.sleep(1000)
                        seconds-=1000
                    else:
                        time.sleep(seconds)
                        seconds=0
                    
            time.sleep(seconds)
            print "processing job..."
            getattr(self,event_name)()
            print "finished succesfully."
            self.find_next(event_name)

from django.db.models.loading import get_apps
get_apps()

#########################################################
#########YOU DONT NEED TO CHANGE ANYTHING ABOVE##########
#########################################################

#your optimization starts here
from report.functions import submission_notification

class MyCron(BaseCron):
    def __init__(self,pid):
        BaseCron.__init__(self,pid)
        
        self.add_event("submission_notification_job", 1, "day", round=True)
        
    def submission_notification_job(self):
        submission_notification()
    

"""
you can directly use your project name as we
already imported our project dynamically

make your model imports here like:

from my_site.poll import Poll
from django.contrib.auth.models import User


start your MyCron class here. inherit it from BaseCron above

class MyCron(BaseCron):
    def __init__(self,pid):
        BaseCron.__init__(self,pid)
        self.add_event("test_job",3,"minute",round=True)
        self.add_event("another_test_job", 1 ,"day",round=True)
        
    def test_job(self):
        Entry.objects.all()

    def another_test_job(self):
        super_users=User.objects.filter(is_superuser=True)
        super_users.delete()


thats all you have to do with this script... read details for more info.

####DETAILS#####

we added a test_job function which is going to run in every three minutes and
will be rounded minutely

we addedn a another test_job function add that will run on every day  at
midnight bacause we rounded it to its period compenent(day) .

    
add_event function adds  a new job to schedule.
    -first argument is function name
    -second is period length
    -third is period component ("second","minute","hour","day","month" or "year"
    -last one tells if time should be rounded to period component otherwise
     function will be called without taking care of component head.
    

name this script and put this script in your projects folder to the same level  with
your settings.py. a pid file will be automatically created into your project's
folder

#####SHELL COMMANDS######

to start:
python deamon.py start

to restart:
python deamon.py restart

to stop:
python deamon.py stop

if you are running on a windows environment or just want to test how it works
use:
python deamon.py run

"""


if __name__ == "__main__":

    daemon = MyCron(os.path.join(os.path.split(DIR)[0],'django-cron-daemon.pid'))
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'run'== sys.argv[1]:
            daemon.run()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart|run" % sys.argv[0]
        sys.exit(2)

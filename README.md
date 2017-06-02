Technical implementation notes on Luigi limitations and features:

* Luigi assumes idempotency. The practical result of this is that if you run a task and it succeeds, and then you run
 it again, Luigi will not run your task the second time because it assumes that the results from the first run are 
 still correct. We are pipelining notebook executions, which usually occur, by definition, in-place. 
 
  Since we can't very well delete the original notebook file, this means that we need to make copies of the original
   notebooks that we are executing, and run the Luigi process across those---purging them beforehand as necessary.
* Everything in Luigi has to be couched in terms of interactions between storage targets. These can be files or they 
can be SQL tables (and a lot of other things), but there's always some sort of storage layer involved. So you can't 
for example pass around Python data (unless you pickle it first). This is done to ensure atomicity.
* Luigi tasks are meant to be launched from the command line. So they can accept parameters made out of Python data 
structures, but the launcher task must receive only parameters expressable on the command line (basically just 
strings and ints and the like). This means that it's not possible to plug-and-play an e.g. `requires` parameter from 
above.

  Getting around this requires wrapping your Luigi tasks in another layer of abstraction, which is our exercise here 
  regardless.
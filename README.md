# cursor-hand-tracking
Move and use cursor using right hand. The program can run using left hand with a little tweak but we have yet to figure out how to get it to detect left or right hand by itself.
1. Use index to move cursor
2. Middle and index finger together to make a click:
  2.a. click only registers when tips of index and middle fingers are close
3. Use thumb and index finger to change volume
  3.a. distance between thumb and index finger determines the volume level
  3.b. Volume changes only on the program output screen when pinkie is up
  3.c. Volume has been smoothened, so only increases or decreases by value of 5, smoothening can be changed by simply changing the variable value
  3.d. lower your pinkie to set the volume to PC's master volume

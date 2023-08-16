miller.john 
README.md
3700 Proj 2

FTP Client

High-level approach:
I modified my client class from the previous project to work with raw binary data if necessary, and designed two new classes for this project. First, I made a Response class for parsing responses from the server, to make it easier to see when errors occured and to read information from the response like an ip or port number. The second, main class I created was the FTPClient class which creates the necessary connections and runs the various operations.

Challenges:
One thing I had a lot of difficulty with during this project was receiving the right message at the right time. This is because I didn't understand the ftp so the more I learned the better ordered my send/recvs became. 

Testing:
I tested my program by running all the commands on the test server and uploading/downloading text files and jpg images. I tested extensively during the coding process to make sure I was going in the right direction.

import java.io.*;
import java.net.*;
import java.nio.*;
import java.nio.channels.*;
import java.nio.charset.*;
import java.util.*;

public class ChatServer
{
  // A pre-allocated buffer for the received data
  static private final ByteBuffer buffer = ByteBuffer.allocate( 16384 );

  // Decoder for incoming text -- assume UTF-8
  static private final Charset charset = Charset.forName("UTF8");
  static private final CharsetDecoder decoder = charset.newDecoder();
  static private final CharsetEncoder enc = Charset.forName("US-ASCII").newEncoder();

  static private List<Socket> Clients = new ArrayList<Socket>();
  static private ArrayList<ArrayList<SocketChannel>> Rooms = new ArrayList<ArrayList<SocketChannel>>();
  static private Map<SocketChannel, String> SocketToStatus = new HashMap<SocketChannel, String>();
  static private Map<String, Integer> RoomNameToIndex = new HashMap<String, Integer>();
  static private Map<String, Integer> UsernameToRoom = new HashMap<String, Integer>();
  static private Map<String, Boolean> TakenUsernames = new HashMap<String, Boolean>();
  static private Map<SocketChannel, String> SocketToUsername = new HashMap<SocketChannel, String>();
  static private Map<String, SocketChannel> UsernameToSocket = new HashMap<String, SocketChannel>();

  static private String lastNick = "Default";
  static private Boolean enterBeforeEOF = false;

  static public void main( String args[] ) throws Exception {
    // Parse port from command line
    int port = Integer.parseInt( args[0] );

    try {
      // Instead of creating a ServerSocket, create a ServerSocketChannel
      ServerSocketChannel ssc = ServerSocketChannel.open();

      // Set it to non-blocking, so we can use select
      ssc.configureBlocking(false);

      // Get the Socket connected to this channel, and bind it to the
      // listening port
      ServerSocket ss = ssc.socket();
      InetSocketAddress isa = new InetSocketAddress(port);
      ss.bind(isa);

      // Create a new Selector for selecting
      Selector selector = Selector.open();

      // Register the ServerSocketChannel, so we can listen for incoming
      // connections
      ssc.register(selector, SelectionKey.OP_ACCEPT);
      System.out.println("Listening on port " + port);

      while (true) {
        // See if we've had any activity -- either an incoming connection,
        // or incoming data on an existing connection
        int num = selector.select();

        // If we don't have any activity, loop around and wait again
        if (num == 0) {
          continue;
        }

        // Get the keys corresponding to the activity that has been
        // detected, and process them one by one
        Set<SelectionKey> keys = selector.selectedKeys();
        Iterator<SelectionKey> it = keys.iterator();
        while (it.hasNext()) {
          // Get a key representing one of bits of I/O activity
          SelectionKey key = it.next();

          // What kind of activity is it?
          if ((key.readyOps() & SelectionKey.OP_ACCEPT) ==
            SelectionKey.OP_ACCEPT) {

            // It's an incoming connection.  Register this socket with
            // the Selector so we can listen for input on it
            Socket s = ss.accept();
            Clients.add(s);
            SocketToUsername.put(s.getChannel(), "No Name");
            UsernameToSocket.put("No Name", s.getChannel());
            SocketToStatus.put(s.getChannel(), "init");
            System.out.println("Got connection from " + s);

            // Make sure to make it non-blocking, so we can use a selector
            // on it.
            SocketChannel sc = s.getChannel();
            sc.configureBlocking( false );

            // Register it with the selector, for reading
            sc.register(selector, SelectionKey.OP_READ);

          } else if ((key.readyOps() & SelectionKey.OP_READ) ==
            SelectionKey.OP_READ) {

            SocketChannel sc = null;

            try {

              // It's incoming data on a connection -- process it
              sc = (SocketChannel)key.channel();
              boolean ok = processInput( sc );

              // If the connection is dead, remove it from the selector
              // and close it
              if (!ok) {
                key.cancel();

                Socket s = null;
                try {
                  s = sc.socket();
                  System.out.println("Closing connection to " + s);
                  s.close();
                } catch( IOException ie ) {
                  System.err.println("Error closing socket " + s + ": " + ie);
                }
              }

            } catch( IOException ie ) {

              // On exception, remove this channel from the selector
              key.cancel();

              try {
                sc.close();
              } catch( IOException ie2 ) { System.out.println( ie2 ); }

              System.out.println("Closed " + sc);
            }
          }
        }

        // We remove the selected keys, because we've dealt with them.
        keys.clear();
      }
    } catch( IOException ie ) {
      System.err.println( ie );
    }
  }

  static private void SendMessageToClient(String message, SocketChannel sc) throws Exception {
    ByteBuffer buf = ByteBuffer.allocate(4000);
    buf.clear();
    buf.put(message.getBytes());

    buf.flip();
    while(buf.hasRemaining()) { sc.write(buf); }
  }

  static private boolean ChangeNickClient(String username, SocketChannel sc, String lastNick) throws Exception {
    // if the username is already in use, send error
    if(TakenUsernames.containsKey(username)) { 
      SendMessageToClient("ERROR\n", sc); 
      return false; 
    }
    // otherwise, change it
    else {
      SocketToUsername.put(sc, username);
      UsernameToSocket.put(username, sc);
      // free the previous username so it can be used now
      TakenUsernames.remove(lastNick);
      TakenUsernames.put(username, true);
      SendMessageToClient("OK\n", sc);
      if(SocketToStatus.get(sc).equals("init")) { SocketToStatus.put(sc, "outside"); }
      return true;
    }
  }

  static private void JoinRoom(String roomName, SocketChannel sc) {
    SocketToStatus.put(sc, "inside");
    int roomIndex = RoomNameToIndex.get(roomName);
    // Add user to room
    Rooms.get(roomIndex).add(sc);
    // Associate a username to a room for when we want to see if a user belongs to a room
    UsernameToRoom.put(SocketToUsername.get(sc), roomIndex);
  }

  static private void LeaveRoom(SocketChannel sc, boolean bye) throws Exception {
    SocketToStatus.put(sc, "outside");
    // if the user is quitting the chat, we do not send the ok message
    if(!bye) { SendMessageToClient("OK\n", sc); }
    // if the user doesnt belong to any room, it cant leave.
    if(!UsernameToRoom.containsKey(SocketToUsername.get(sc))) { return; }
    String username = SocketToUsername.get(sc);
    int roomIndex = UsernameToRoom.get(username);
    // remove username association with a room
    UsernameToRoom.remove(username);
    // remove user from room
    Rooms.get(roomIndex).remove(sc);
    // tell the other members of the room, user X has just left
    LeftOrJoinedRoomNotice(roomIndex, "LEFT ", sc);
  }

  static private void LeftOrJoinedRoomNotice(int roomIndex, String message, SocketChannel sc) throws Exception {
    String username = SocketToUsername.get(sc);
    for(int i = 0; i < Rooms.get(roomIndex).size(); i++) {
      SocketChannel userInRoom = Rooms.get(roomIndex).get(i);
      if(sc != userInRoom) { SendMessageToClient(message + username + "\n", userInRoom); }
    }
  }

  static private void CreateRoom(SocketChannel sc, String roomName){
    // Create a room which is a list of socket channels inside our room list.
    Rooms.add(new ArrayList<SocketChannel>());
    int roomIndex = Rooms.size()-1;
    // Associate a roomname to a room index
    RoomNameToIndex.put(roomName, roomIndex);
    JoinRoom(roomName, sc);
  }

  static private void CloseSocket(SocketChannel sc) throws Exception {
    SendMessageToClient("BYE\n", sc);
    System.out.println("Closing connection to " + sc.socket());
    sc.socket().close();
  }

  static private void SendPrivateMsg(String from, String to, String message) throws Exception {
    SendMessageToClient("PRIVATE " + from + message + "\n", UsernameToSocket.get(to));
  }

  // Just read the message from the socket and send it to stdout
  static private boolean processInput(SocketChannel sc) throws Exception {
    // Read the message to the buffer
    buffer.clear();
    // This take of data delineation, it take care of cases like, if you have /ni<CTRL-D>ck <CTRL-D> testUser, it will only process /nick testUser
    try {
      while(true) {
        ByteBuffer tmp = ByteBuffer.allocate(1);
        sc.read(tmp);
        tmp.rewind();
        byte cur = tmp.get();
        if(cur == 0) {
          if(enterBeforeEOF) { break; }
          else { continue; }
        }
        buffer.put(cur);
        if(cur == 10) { enterBeforeEOF = true; break; }
        else { enterBeforeEOF = false; }
      }
    }
    catch(Exception e) {}

    buffer.flip();

    // If no data, close the connection
    if (buffer.limit()==0) { return false; }

    // Decode and print the message to stdout
    String message = decoder.decode(buffer).toString().replace("\n", "");

    if(message.startsWith("//")) { message = message.substring(1); }
    // User wants to change nick
    if(message.startsWith("/nick")) {
      String username = message.split(" ")[1].replace("\n", "");

      // If the user is not in any room, send an okay or an error only to him/her.
      lastNick = SocketToUsername.get(sc);
      if(!UsernameToRoom.containsKey(SocketToUsername.get(sc))) { 
      	ChangeNickClient(username, sc, lastNick); 
      }
      else {
        int roomIndex = UsernameToRoom.get(lastNick);
        // if the username changed successfully, we can alert the others
        if(ChangeNickClient(username, sc, lastNick)) {
          // Remove the connection of the previous username to any room
          UsernameToRoom.remove(lastNick);
          // Add a connection of the new username to the same room
          UsernameToRoom.put(username, roomIndex);
          for(int i = 0; i < Rooms.get(roomIndex).size(); i++) {
            SocketChannel sock = Rooms.get(roomIndex).get(i);
            if(sc != sock) {
              String newUsername = message.split(" ")[1].replace("\n", "");
              SendMessageToClient("NEWNICK " + lastNick + " " + newUsername + "\n", sock);
            }
          }
        }
      }
    }
    // else if the user already has a name
    else if(!SocketToStatus.get(sc).equals("init")) {
      // User wants to join a room
      if(message.startsWith("/join")){

        // Get room name
        String roomName = message.split(" ")[1].replace("\n", "");

        // If the user already belongs to a room change rooms
        if(UsernameToRoom.containsKey(SocketToUsername.get(sc))) {
          LeaveRoom(sc, true);
          // if that room doesnt exist yet
          if(!RoomNameToIndex.containsKey(roomName)) { CreateRoom(sc, roomName); }
          else { JoinRoom(roomName, sc); }
        }
        // If room does not exist, create it.
        else if(!RoomNameToIndex.containsKey(roomName)) { CreateRoom(sc, roomName); }
        // Else, join room.
        else { JoinRoom(roomName, sc); }

        SendMessageToClient("OK\n", sc);

        // Tell the other members of the room that user X has just joined.
        int roomIndex = UsernameToRoom.get(SocketToUsername.get(sc));
        String username = SocketToUsername.get(sc);
        LeftOrJoinedRoomNotice(roomIndex, "JOINED ", sc);
      }
      else if(message.startsWith("/leave")) { LeaveRoom(sc, false); }
      else if(message.startsWith("/bye")) { LeaveRoom(sc, true); CloseSocket(sc); }
      else if(message.startsWith("/priv")) {
        String sender = SocketToUsername.get(sc);
        String receiver = message.split(" ")[1];
        if(!UsernameToSocket.containsKey(receiver)) { SendMessageToClient("ERROR\n", sc); }
        else {
          String privateMessage = message.substring(message.indexOf(" ", 6));
          SendPrivateMsg(sender, receiver, privateMessage);
          SendMessageToClient("OK\n", sc);
        }
      }
      else if(SocketToStatus.get(sc).equals("inside")) {
        // If the user belongs to a room, send his message to all the other members of that room.
        if(UsernameToRoom.containsKey(SocketToUsername.get(sc))) {
          int roomIndex = UsernameToRoom.get(SocketToUsername.get(sc));
          for(int i = 0; i < Rooms.get(roomIndex).size(); i++) {
            SocketChannel userInRoom = Rooms.get(roomIndex).get(i);
            String username = SocketToUsername.get(sc);
            SendMessageToClient("MESSAGE " + username + " " + message + "\n", userInRoom);
          }
        }
        else { SendMessageToClient(message + "\n", sc); }
      }
      else { SendMessageToClient("ERROR\n", sc); }
    }
    else { SendMessageToClient("ERROR\n", sc); }
  	return true;
  }
  static void print(Object msg) { System.out.print(msg); }
}

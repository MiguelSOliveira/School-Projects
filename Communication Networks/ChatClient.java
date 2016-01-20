import java.io.*;
import java.net.*;
import java.util.*;
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;


public class ChatClient {

  // Variaveis relacionadas com a interface grafica --- * NaO MODIFICAR *
  JFrame frame = new JFrame("Chat Client");
  private JTextField chatBox = new JTextField();
  private JTextArea chatArea = new JTextArea();
  // --- Fim das variaveis relacionadas coma interface grafica

  // Se for necessario adicionar variaveis ao objecto ChatClient, devem
  // ser colocadas aqui

  private Socket socket;
  private String changedNick;
  private OutputStream os;
  private OutputStreamWriter osw;
  private BufferedWriter bw;
  private String server;
  private int port;
  private String lastRequest = "";
  private String lastNick = "";
  private BufferedReader inFromServer;


  // Metodo a usar para acrescentar uma string Ã  caixa de texto
  // * NaO MODIFICAR *
  public void printMessage(final String message) {
    chatArea.append(message + '\n');
  }

  // Construtor
  public ChatClient(String server, int port) throws IOException {

        // InicializaÃ§Ã£o da interface grafica --- * NaO MODIFICAR *
    frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
    JPanel panel = new JPanel();
    panel.setLayout(new BorderLayout());
    panel.add(chatBox);
    frame.setLayout(new BorderLayout());
    frame.add(panel, BorderLayout.SOUTH);
    frame.add(new JScrollPane(chatArea), BorderLayout.CENTER);
    frame.setSize(500, 300);
    frame.setVisible(true);
    chatArea.setEditable(false);
    chatBox.setEditable(true);
    chatBox.addActionListener(new ActionListener() {
      @Override
      public void actionPerformed(ActionEvent e) {
        try {
          newMessage(chatBox.getText());
        } catch (IOException ex) {
        } finally {
         chatBox.setText("");
       }
     }
   });
    // --- Fim da inicializacao da interface grafica

    // Se for necessario adicionar codigo de inicializacao ao
    // construtor, deve ser colocado aqui

    this.server = server;
    this.port = port;
  }


    // Metodo invocado sempre que o utilizador insere uma mensagem
    // na caixa de entrada
  public void newMessage(String message) throws IOException {
    // PREENCHER AQUI com codigo que envia a mensagem ao servidor
    lastRequest = message;
    bw.write(message + '\n');
    bw.flush();
  }

  public void HandleMessageFromServer(String message) {

    String firstToken = message.split(" ")[0], username = "";
    switch(firstToken) {
      case "OK":
      case "ERROR":
        String lastRequestTokens[] = lastRequest.split(" ");

        switch(lastRequestTokens[0]) {
          case "/nick":
            if(firstToken.startsWith("OK")) { printMessage("You have changed username to " + lastRequestTokens[1]); }
            else { printMessage("Username is already taken"); } break;
          case "/join": 
            if(firstToken.startsWith("OK")) { printMessage("You have joined room " + lastRequestTokens[1]); }
            else { printMessage("You must first choose a username before anything else"); } break;
          case "/leave": 
            if(firstToken.startsWith("OK")) { printMessage("You have left the room"); }
            else { printMessage("You are not in any room"); } break;
          case "/priv": 
            if(firstToken.startsWith("OK")) { printMessage("You have sent a PM to " + lastRequestTokens[1]); }
            else { printMessage("User does not exist"); } break;
          default:
            printMessage("Cannot talk whilst not in any room");
        }
      case "JOINED":
      case "LEFT":
        username = message.split(" ")[1];
        printMessage("User " + username + " has "+ firstToken.toLowerCase() +" the room"); break;
      case "NEWNICK":
        String oldUsername = message.split(" ")[1];
        String newUsername = message.split(" ")[2];
        printMessage("User " + oldUsername + " has changed username to " + newUsername); break;
      case "PRIVATE":
        username = message.split(" ")[1];
        printMessage("PM from " + username + ": " + message.substring(message.indexOf(" ", 8))); 
        break;
      case "MESSAGE":
        username = message.split(" ")[1];
        printMessage(username + ": " + message.substring(message.indexOf(" ", 8)));
        break; 
      default: 
        printMessage(message);
    }
  }


    // Metodo principal do objecto
  public void run() throws IOException {
    // PREENCHER AQUI

    socket = new Socket(this.server, this.port);
    inFromServer = new BufferedReader(new InputStreamReader(socket.getInputStream()));
    os = socket.getOutputStream();
    osw = new OutputStreamWriter(os);
    bw = new BufferedWriter(osw);

    ServerCommunication sc = new ServerCommunication();
    sc.run();
  }


    // Instancia o ChatClient e arranca-o invocando o seu metodo run()
    // * NaO MODIFICAR *
  public static void main(String[] args) throws IOException {
    ChatClient client = new ChatClient(args[0], Integer.parseInt(args[1]));
    client.run();
  }

  class ServerCommunication implements Runnable {

    public void run() {
      while(true) {
        try {
          String messageFromServer = inFromServer.readLine();
          if(messageFromServer != null) { HandleMessageFromServer(messageFromServer); }
        } catch(Exception e){}
      }
    }
  }
  static void print(Object msg) { System.out.print(msg); }
}
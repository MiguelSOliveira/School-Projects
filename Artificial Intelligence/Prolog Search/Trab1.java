import java.util.*;

class Flight {
 String from, to, daySum;
 LinkedList<String> days = new LinkedList<String>();
 LinkedList<String> flightNum = new LinkedList<String>();
 LinkedList<String> depTime = new LinkedList<String>();
 LinkedList<String> arrTime = new LinkedList<String>();

 Flight(String f, String t, LinkedList<String> fn, LinkedList<String> dt, LinkedList<String> at, LinkedList<String> d, String ds){
  from = f;
  to = t;
  flightNum = fn;
  depTime = dt;
  arrTime = at;
  days = d;
  daySum = ds;
 }
}

public class Trab3{

 public static boolean vis[] = new boolean[5], graph[][] = new boolean[5][5], first = true, AllFlightsAdded;
 public static HashMap<String, Integer> index = new HashMap<>();
 public static HashMap<Integer, String> stringIndex = new HashMap<>();
 public static LinkedList<String> FlightNumbers = new LinkedList<String>();
 public static LinkedList<String> DepTimes = new LinkedList<String>();
 public static Flight flights[] = new Flight[12];
 public static int k = 1, previousFlight;
 public static int[] path = {-1,-1,-1,-1,-1,-1,-1,-1,-1};
 public static HashSet<String> s1CharSet = new HashSet<String>(), s2CharSet = new HashSet<String>();
 public static String daysAvailable = "";

 static boolean transferTime(String t1, String t2){
  int h1, h2, min1, min2, diffMins;
  String[] temp1, temp2;

  temp1 = t1.split(":");
  temp2 = t2.split(":");
  h1 = Integer.parseInt(temp1[0]);
  min1 = Integer.parseInt(temp1[1]);
  h2 = Integer.parseInt(temp2[0]);
  min2 = Integer.parseInt(temp2[1]);

  if(h1 < h2){
   diffMins = (h2-h1) * 60 + (min2 - min1);
  }
  else {
   diffMins = ((h2+24) - h1) * 60 + (min2 - min1);
  }

  if(diffMins >= 40) return true;
  return false;
 }


 static void dfs(int from, int to){
  int targetDest, flightFound = -1;
  vis[from] = true;

  for(int i = 0; i < 5; i++){
   if(graph[from][i] && !vis[i]){

    if(graph[from][to]) targetDest = to;
    else targetDest = i;

    for(int j = 0; j < flights.length; j++){
     if(flights[j].from.equals(stringIndex.get(from)) && flights[j].to.equals(stringIndex.get(targetDest))) {
      flightFound = j;
      break;
     }
    }

    // If a flight was found
    if(flightFound != -1){

     int indexOfList = -1;
     // Check for intersecting days
     if(!AllFlightsAdded && !first){
      String string1 = flights[flightFound].daySum;
      String string2 = flights[previousFlight].daySum;
      String[] s1 = string1.split(",");
      String[] s2 = string2.split(",");
      for(String day: s1) s1CharSet.add(day);
      for(String day: s2) s2CharSet.add(day);
      s1CharSet.retainAll(s2CharSet);
     }

      if(!first) daysAvailable = Arrays.toString(s1CharSet.toArray(new String[s1CharSet.size()]));
      else daysAvailable = flights[flightFound].daySum;

      // Find index of flight number
      for(int k = 0; k < flights[flightFound].flightNum.size(); k++) {
       for(String day: flights[flightFound].days.get(k).split(",")){
        if(daysAvailable.contains(day)){ indexOfList = k; break; }
       }
      }

     // If there are intersecting days
     if(s1CharSet.size() != 0 || first){
      if(graph[from][to]) {
       path[k++] = to;
       if(!AllFlightsAdded) {
        FlightNumbers.add(flights[flightFound].flightNum.get(indexOfList));
        if(first || transferTime(DepTimes.getLast(), flights[flightFound].depTime.get(indexOfList))){
         DepTimes.add(flights[flightFound].depTime.get(indexOfList));
        }
       }
       AllFlightsAdded = true;
       return;
      }

      if(indexOfList != -1){
       previousFlight = flightFound;
       if(!AllFlightsAdded) {
        FlightNumbers.add(flights[flightFound].flightNum.get(indexOfList));
        if(first || transferTime(DepTimes.getLast(), flights[flightFound].depTime.get(indexOfList))){
         DepTimes.add(flights[flightFound].depTime.get(indexOfList));
        }
       }
       first = false;
       path[k++] = i;
       if(i == to) return;
       dfs(i, to);
      }
     }
    }
   }
  }
 }

 static void CreateFlights(){
  LinkedList<String> flightNum = new LinkedList<String>();
  LinkedList<String> arrTime = new LinkedList<String>();
  LinkedList<String> depTime = new LinkedList<String>();
  LinkedList<String> days = new LinkedList<String>();
  String daySum;

  flightNum.add("ba4733");
  flightNum.add("ba4733");
  flightNum.add("ba4833");
  depTime.add("9:40");
  depTime.add("13:40");
  depTime.add("19:40");
  arrTime.add("10:50");
  arrTime.add("14:50");
  arrTime.add("20:50");
  days.add("mo");
  days.add("tu");
  days.add("mo,tu");
  daySum = "mo,tu,we,th,fr,sa,su";
  flights[0] = new Flight("edinburgh", "london", flightNum, depTime, arrTime, days, daySum);
  flightNum = new LinkedList<String>();
  arrTime = new LinkedList<String>();
  depTime = new LinkedList<String>();
  days = new LinkedList<String>();

  flightNum.add("ju201");
  flightNum.add("ju213");
  depTime.add("13:20");
  depTime.add("13:20");
  arrTime.add("16:20");
  arrTime.add("16:20");
  days.add("fr");
  days.add("su");
  daySum = "fr,su";
  flights[1] = new Flight("london", "ljubljana", flightNum, depTime, arrTime, days, daySum);
  flightNum = new LinkedList<String>();
  arrTime = new LinkedList<String>();
  depTime = new LinkedList<String>();
  days = new LinkedList<String>();

  flightNum.add("az458");
  flightNum.add("ba511");
  depTime.add("9:10");
  depTime.add("12:20");
  arrTime.add("10:00");
  arrTime.add("13:10");
  days.add("mo,tu,we,th,fr,sa,su");
  days.add("mo,tu,we,th,fr,sa,su");
  daySum = "mo,tu,we,th,fr,sa,su";
  flights[2] = new Flight("milan", "london", flightNum, depTime, arrTime, days, daySum);
  flightNum = new LinkedList<String>();
  arrTime = new LinkedList<String>();
  depTime = new LinkedList<String>();
  days = new LinkedList<String>();

  flightNum.add("sr621");
  flightNum.add("sr623");
  depTime.add("9:25");
  depTime.add("12:45");
  arrTime.add("10:15");
  arrTime.add("13:35");
  days.add("mo,tu,we,th,fr,sa,su");
  days.add("mo,tu,we,th,fr,sa,su");
  daySum = "mo,tu,we,th,fr,sa,su";
  flights[3] = new Flight("milan", "zurich", flightNum, depTime, arrTime, days, daySum);
  flightNum = new LinkedList<String>();
  arrTime = new LinkedList<String>();
  depTime = new LinkedList<String>();
  days = new LinkedList<String>();

  flightNum.add("ba613");
  flightNum.add("sr806");
  depTime.add("9:00");
  depTime.add("16:10");
  arrTime.add("9:40");
  arrTime.add("16:55");
  days.add("mo,tu,we,th,fr,sa");
  days.add("mo,tu,we,th,fr,su");
  daySum = "mo,tu,we,th,fr,sa,su";
  flights[4] = new Flight("zurich", "london", flightNum, depTime, arrTime, days, daySum);
  flightNum = new LinkedList<String>();
  arrTime = new LinkedList<String>();
  depTime = new LinkedList<String>();
  days = new LinkedList<String>();

  flightNum.add("ba4732");
  flightNum.add("ba4752");
  flightNum.add("ba4822");
  depTime.add("9:40");
  depTime.add("11:40");
  depTime.add("18:40");
  arrTime.add("10:50");
  arrTime.add("12:50");
  arrTime.add("19:50");
  days.add("mo,tu,we,th,fr,sa,su");
  days.add("mo,tu,we,th,fr,sa,su");
  days.add("mo,tu,we,th,fr");
  daySum = "mo,tu,we,th,fr,sa,su";
  flights[5] = new Flight("london", "edinburgh", flightNum, depTime, arrTime, days, daySum);
  flightNum = new LinkedList<String>();
  arrTime = new LinkedList<String>();
  depTime = new LinkedList<String>();
  days = new LinkedList<String>();

  flightNum.add("ba614");
  flightNum.add("sr805");
  depTime.add("9:10");
  depTime.add("14:45");
  arrTime.add("11:45");
  arrTime.add("17:20");
  days.add("mo,tu,we,th,fr,sa,su");
  days.add("mo,tu,we,th,fr,sa,su");
  daySum = "mo,tu,we,th,fr,sa,su";
  flights[6] = new Flight("london", "zurich", flightNum, depTime, arrTime, days, daySum);
  flightNum = new LinkedList<String>();
  arrTime = new LinkedList<String>();
  depTime = new LinkedList<String>();
  days = new LinkedList<String>();

  flightNum.add("ba510");
  flightNum.add("az459");
  depTime.add("8:30");
  depTime.add("11:00");
  arrTime.add("11:20");
  arrTime.add("13:50");
  days.add("mo,tu,we,th,fr,sa,su");
  days.add("mo,tu,we,th,fr,sa,su");
  daySum = "mo,tu,we,th,fr,sa,su";
  flights[7] = new Flight("london", "milan", flightNum, depTime, arrTime, days, daySum);
  flightNum = new LinkedList<String>();
  arrTime = new LinkedList<String>();
  depTime = new LinkedList<String>();
  days = new LinkedList<String>();

  flightNum.add("ju322");
  depTime.add("11:30");
  arrTime.add("12:40");
  days.add("tu,th");
  daySum = "tu,th";
  flights[8] = new Flight("ljubljana", "zurich", flightNum, depTime, arrTime, days, daySum);
  flightNum = new LinkedList<String>();
  arrTime = new LinkedList<String>();
  depTime = new LinkedList<String>();
  days = new LinkedList<String>();

  flightNum.add("yu200");
  flightNum.add("yu212");
  depTime.add("11:10");
  depTime.add("11:25");
  arrTime.add("12:20");
  arrTime.add("12:20");
  days.add("fr");
  days.add("su");
  daySum = "fr,su";
  flights[9] = new Flight("ljubljana", "london", flightNum, depTime, arrTime, days, daySum);
  flightNum = new LinkedList<String>();
  arrTime = new LinkedList<String>();
  depTime = new LinkedList<String>();
  days = new LinkedList<String>();

  flightNum.add("yu323");
  depTime.add("13:30");
  arrTime.add("14:40");
  days.add("tu,th");
  daySum = "tu,th";
  flights[10] = new Flight("zurich", "ljubljana", flightNum, depTime, arrTime, days, daySum);
  flightNum = new LinkedList<String>();
  arrTime = new LinkedList<String>();
  depTime = new LinkedList<String>();
  days = new LinkedList<String>();

  flightNum.add("sr620");
  depTime.add("7:55");
  arrTime.add("8:45");
  days.add("mo,tu,we,th,fr,sa,su");
  daySum = "mo,tu,we,th,fr,sa,su";
  flights[11] = new Flight("zurich", "milan", flightNum, depTime, arrTime, days, daySum);
  flightNum = new LinkedList<String>();
  arrTime = new LinkedList<String>();
  depTime = new LinkedList<String>();
  days = new LinkedList<String>();
 }

 public static void main(String[] args){
  Scanner sc = new Scanner(System.in);


  // Creating hashmap and "reverse" hashmap
  index.put("edinburgh", 0);
  index.put("london", 1);
  index.put("ljubljana", 2);
  index.put("milan", 3);
  index.put("zurich", 4);
  stringIndex.put(0, "edinburgh");
  stringIndex.put(1, "london");
  stringIndex.put(2, "ljubljana");
  stringIndex.put(3, "milan");
  stringIndex.put(4, "zurich");

  // Direct flights graph
  graph[index.get("edinburgh")][index.get("london")] = true;
  graph[index.get("london")][index.get("edinburgh")] = true;
  graph[index.get("london")][index.get("ljubljana")] = true;
  graph[index.get("london")][index.get("zurich")] = true;
  graph[index.get("london")][index.get("milan")] = true;
  graph[index.get("ljubljana")][index.get("zurich")] = true;
  graph[index.get("ljubljana")][index.get("london")] = true;
  graph[index.get("milan")][index.get("london")] = true;
  graph[index.get("milan")][index.get("zurich")] = true;
  graph[index.get("zurich")][index.get("ljubljana")] = true;
  graph[index.get("zurich")][index.get("london")] = true;
  graph[index.get("zurich")][index.get("milan")] = true;

  // Creating array of flights database
  CreateFlights();


  String from, to;
  from = sc.nextLine();
  to = sc.nextLine();
  System.out.println("From: " + from);
  System.out.println("To: " + to);

  path[0] = index.get(from);
  dfs(index.get(from), index.get(to));

  System.out.println("Days available: " + daysAvailable);

  System.out.print("Example Route: ");
  for(int k = 0; k < FlightNumbers.size()+1; k++){
   if(FlightNumbers.isEmpty()){ System.out.println(); break; }
   System.out.print(stringIndex.get(path[k]) + "-" + stringIndex.get(path[k+1]) + ":" + FlightNumbers.removeFirst() + ":" + DepTimes.removeFirst() + " ");
  }
  System.out.println();
 }
}

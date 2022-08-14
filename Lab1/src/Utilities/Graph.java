package Utilities;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;



public class Graph {
	public static Map<String,Node> buildGraph(){
		//System.out.println("Building graph");
		
		JSONObject graphJson = readJsonFile("D:\\NTU\\year2sem2\\CZ3005\\Lab\\Lab1 report\\Lab1\\src\\Tasks\\G.json");
		Map<String, Map<String, Double>> distWeightMap = buildWeightMap("D:\\NTU\\year2sem2\\CZ3005\\Lab\\Lab1 report\\Lab1\\src\\Tasks\\Dist.json");
		Map<String, Map<String, Double>> energyWeightMap = buildWeightMap("D:\\NTU\\year2sem2\\CZ3005\\Lab\\Lab1 report\\Lab1\\src\\Tasks\\Cost.json");

	    
	    Map<String, Node> nodesMap = new HashMap<>();
	    
	    //"1": ["1363", "12", "2"], G JSON
	    for(Object keyObj : graphJson.keySet()) {
	    	
	    	//get the all neighbor of current Node into array
	    	JSONArray neighbors = (JSONArray) graphJson.get(keyObj);
	    	
	    	String curKeyNode = keyObj.toString();
	    	if(!nodesMap.containsKey(curKeyNode)){	
	    		//System.out.println(curKeyNode + " : " + neighbors);
	    		//<curKeyNodeID,curNode>  nodesMap
	    		nodesMap.put(curKeyNode, new Node(curKeyNode));
	    	}
	    	
	    	
	    	//get all the neighbors of current Node
	    	Node curNode = nodesMap.get(curKeyNode);
	    	
	    	//cost for Distance and Energy
	    	//<CurNode,cost curNode to targetNode>
	    	Map<Node,EdgeCosts> neightboursNodes = new HashMap<>();
	    	
	    	//going through the neighbor JSON Array
	    	//add all the neighbors of CurNode into NodeMap if they are not inside yet
	    	//Eg) the adjacent nodes to from Node1 are ["1363", "12", "2"]
	    	for(Object neighbor : neighbors) {
	    		String curNeighbourKey = neighbor.toString();
	    		if(!nodesMap.containsKey(curNeighbourKey)) {
	    			nodesMap.put(curNeighbourKey, new Node(curNeighbourKey));
	    		}
	    		/*Eg)from Node1->neighbor are <Node2,distance & energy Cost>
	    		from Node1 neighbor are <Node12,distance & energy Cost>
	    		from Node1 neighbor are <Node1363,distance & energy Cost>
	    		*/
	    		//System.out.println("curNodeId " + curKeyNode);
	    		//System.out.println("neighborNodeId " + neighbor);
	    		//double dist = distWeightMap.get("1").get("2");
	    		//double energy = energyWeightMap.get("1").get("2");
	    		//System.out.println("dist = " + dist);
	    		//System.out.println("energy = " + energy);
	    		neightboursNodes.put(nodesMap.get(curNeighbourKey), 
	    				new EdgeCosts(distWeightMap.get(curKeyNode).get(curNeighbourKey),energyWeightMap.get(curKeyNode).get(curNeighbourKey)));
	    	}
	    	
	    	//Node has a mapped reference to its neighbors with Distance/Energy Costs 
	    	curNode.neighbours = neightboursNodes;
	    }
	    /*
	     * <NodeID,Node>
	     * Node->neighbors are <Node2,distance & energy Cost>
	     */
		return nodesMap;
	}

	public static Map<String, Map<String, Double>> buildWeightMap(String filepath) {
		//build the distance and energy weight
		//both JSON are of same format
		JSONObject weightJson = readJsonFile(filepath);
		
		Map<String,Map<String,Double>> weightMap = new HashMap<>();
		//System.out.println("Object keyObj : weightJson.keySet()");
		for(Object keyObj : weightJson.keySet()) {
			String FromToEdge = keyObj.toString();
			//need split
			String[] keyFromToEdge = FromToEdge.split(",");
			
			//fromEdge to toEdge cost
			Double cost = Double.valueOf(weightJson.get(keyObj).toString());
			//System.out.println("[" + keyFromToEdge[0] + "," + keyFromToEdge[1] + "]" + " : " + cost);

			//create mapping for fromNode i
			if(!weightMap.containsKey(keyFromToEdge[0])) {
				weightMap.put(keyFromToEdge[0], new HashMap<>());
			}
			weightMap.get(keyFromToEdge[0]).put(keyFromToEdge[1], cost);
		}
		//same for distance and energy
		//format <1, <2,2008>>
		return weightMap;
	}
	
	//"1": [-73530767, 41085396]
	public static Map<String,Coordinate> buildCoordMap(String filepath){
		Map<String, Coordinate>  coordMap = new HashMap<>();
		JSONObject coordJson = readJsonFile(filepath);
		for(Object keyObj : coordJson.keySet()) {
			String keyNodeID = keyObj.toString();
			String coordValues = coordJson.get(keyNodeID).toString().trim();
			//System.out.println("coordValues " + coordValues); [-73530767, 41085396]
			//remove the [  ] brackets and ','
			String[] xyValues = coordValues.substring(1, coordValues.length()-1).split(",");
			//System.out.println(xyValues[0] +  " , "  + xyValues[1]);
			if(!coordMap.containsKey(keyNodeID)) {
				double xCoord = Double.parseDouble(xyValues[0]);
				double yCoord = Double.parseDouble(xyValues[1]);
				Coordinate newCoord = new Coordinate(xCoord, yCoord);
				coordMap.put(keyNodeID, newCoord);
			}
		}
	
		return coordMap;
	}
	
	public static String buildPathStartToEnd(Node endNode) {
		LinkedList<String> path = new LinkedList<String>();
		Node curNode = endNode;
		while(curNode != null) {
			//reconstruct backwards but add to LL in the front so no need reverse
			path.add(0, curNode.id);
			curNode = curNode.parent;
		}
		return pathToString(path);
	
	}
	
	private static String pathToString(List<String> path) {
		StringBuilder sb = new StringBuilder();
		for(int i = 0;i<path.size();i++) {
			if(i == path.size() - 1) {
				//last node
				sb.append(path.get(i));
			}
			else {
				sb.append(path.get(i) + " -> ");
			}
		}
		return sb.toString();
	}
	private static JSONObject readJsonFile(String filepath) {
		// TODO Auto-generated method stub
		try {
			JSONParser parser = new JSONParser();
			// Use JSONObject for simple JSON and JSONArray for array of JSON.
			JSONObject jsonG = (JSONObject) parser.parse(new FileReader(filepath));
			return jsonG;
			
		}
		catch (IOException | ParseException e) {
			// TODO: handle exception
			e.printStackTrace();
		}
		return null;
	}
}

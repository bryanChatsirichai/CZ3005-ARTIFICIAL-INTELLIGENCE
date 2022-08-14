package Tasks;

import java.text.DecimalFormat;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;
import java.util.PriorityQueue;

import Utilities.Graph;
import Utilities.Node;


public class Task1Ver1 {
	//given data set
	//change doubles to 2 decimal place
	private static final DecimalFormat df = new DecimalFormat("0.00");
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		//System.out.println("Starting Task1");
	    //setting up the graph
		System.out.println("Building graph");
		Map<String, Node> graph = Graph.buildGraph();
		
		//start and end node
		final String start = "1";
		final String end = "50";
		
		long startTime = System.nanoTime();
		Node endNode = uniformCostSearch(graph, start, end);
		long endTime = System.nanoTime();
		long executionTime = (endTime - startTime) / 1000000; // NANO to MILLI seconds
		if(endNode == null) {
			System.out.println("No Path from node " + start + " to node " +  end);
			return;
		}
		String path = Graph.buildPathStartToEnd(endNode);
	    
	    System.out.println("---------- Task One ----------");
	    System.out.println("Shortest Path from node " + start + " to node " +  end);
	    System.out.println("Uniform Cost Search UCS algorithm runtime " + executionTime + " milliSec");
	    System.out.println("Total distance cost from node " + start + " to node " +  end + ": " + df.format(endNode.distCost));
	    System.out.println("Total energy cost from node " + start + " to node " +  end + ": " + df.format(endNode.energyCost));
	    System.out.println("Shortest Path from node " + start + " to node " +  end);
		System.out.println(path);
		
		
	}

	//UCS or Dijkstra
	private static Node uniformCostSearch(Map<String,Node> graph, String start,String end) {
	    PriorityQueue<Node> pq = new PriorityQueue<>(new Comparator<Node>() {
			@Override
			public int compare(Node node1, Node node2) {
				return (int) (node1.distCost - node2.distCost);
				
			}
		});
	    
	    //HashMap is used to track which node has been visited or relaxed
	    //Map to also keep track of the Node distance/energy cost from start to it.
	    Map<String,Boolean> visited = new HashMap<>();
	    Map<String,Double> distCost = new HashMap<>();
	    Map<String,Double> energyCost = new HashMap<>();
	   
	    Node startNode = graph.get(start);
	    pq.add(startNode);
	   
	    visited.put(startNode.id, false);
	    distCost.put(startNode.id, 0.0);
	    //energyCost.put(startNode.id, 0.0);
	    
	    
	    while(!pq.isEmpty()) {
	    	Node curNode = pq.poll();
	    	//System.out.println("CurNode " + curNode.id);
	    	if(curNode.id.equals(end)) {
	    		//found end node already no point traverse 
	    		return curNode;
	    	}
	    	if(visited.get(curNode.id) == true) {
	    		//skip already visited(relaxed) node
	    		continue;
	    	}
	    	
	    	//If the map previously contained a mapping for the key, the old value is replaced by the specified value
	    	//mark current node as visited(relaxed)
	    	visited.put(curNode.id,true);
	    	
	    	//small optimization
	    	if(distCost.get(curNode.id) < curNode.distCost) {
	    		continue;
	    	}
	    	
	    	//get all the neighbors of currentNode
	    	//iterate 1 by 1
	    	for(Node neighborNode : curNode.neighbours.keySet()) {
	    		
	    		//cost from startNode to given neighbor node
	    		Double newDistCost = curNode.distCost + curNode.neighbours.get(neighborNode).distEdgeCost;
	    		Double newEnergyCost = curNode.energyCost + curNode.neighbours.get(neighborNode).energyEdgeCost;
	    		if(newDistCost < distCost.getOrDefault(neighborNode.id,Double.MAX_VALUE)) {
	    	
	    			//create mapping to check which node need visit 
	    			visited.put(neighborNode.id, false);
	    	
	    			//update distance from startNode to curNode
	    			distCost.put(neighborNode.id, newDistCost);
	    			neighborNode.distCost = newDistCost;
	    			
	    			//update distance from startNode to curNode
	    			
	    			energyCost.put(neighborNode.id, newEnergyCost);
	    			neighborNode.energyCost = newEnergyCost;
	    			
	    			//keep track of parent so can construct the path from start to end
	    			neighborNode.parent = curNode;
	    			pq.add(neighborNode);
	    		}
	    	}
	    	
	    }
	    
	    return null;
	    /*
	    if(!visited.containsKey(end)) {
	    	//no path found
	    	return null;
	    }
	    else {
	    	//path found to end Node
	    	//System.out.println("Total Distance cost " + distCost.get(end));
	    	//System.out.println("Total Energy cost " + energyCost.get(end));
	    	//return graph.get(end);
	    }
	    */
	}
}

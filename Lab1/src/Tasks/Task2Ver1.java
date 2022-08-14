package Tasks;

import java.text.DecimalFormat;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;

import Utilities.EdgeCosts;
import Utilities.Graph;
import Utilities.Node;


public class Task2Ver1 {
	//change doubles to 2 decimal place
	private static final DecimalFormat df = new DecimalFormat("0.00");
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		//System.out.println("Starting Task1");
	    //setting up the graph
		System.out.println("Building graph");
		Map<String, Node> graph = Graph.buildGraph();
		System.out.println("distWeightMap");
		Map<String, Map<String, Double>> distWeightMap = Graph.buildWeightMap("D:\\NTU\\year2sem2\\CZ3005\\Lab\\Lab1 report\\Lab1\\src\\Tasks\\Dist.json");
		System.out.println("energyWeightMap");
		Map<String, Map<String, Double>> energyWeightMap = Graph.buildWeightMap("D:\\NTU\\year2sem2\\CZ3005\\Lab\\Lab1 report\\Lab1\\src\\Tasks\\Cost.json");
	
		
		//start and end node
		final String start = "1";
		final String end = "50";
		final double energyBudget = 287932;
		long startTime = System.nanoTime();
		Node endNode = uniformCostSearch(graph,distWeightMap,energyWeightMap, start, end,energyBudget);
		long endTime = System.nanoTime();
		long executionTime = (endTime - startTime) / 1000000; // NANO to MILLI seconds
		if(endNode == null) {
			System.out.println("No path from startNode '1' to endNode '50' within energy budget");
			return;
		}
		
	    
	    System.out.println("---------- Task Two ----------");
	    System.out.println("Shortest Path from node " + start + " to node " +  end);
	    System.out.println("Energy Budget of " + energyBudget);
	    System.out.println("Uniform Cost Search UCS algorithm runtime " + executionTime + " milliSec");
	    System.out.println("Total distance cost from node " + start + " to node " +  end + ": " + df.format(endNode.distCost));
	    System.out.println("Total energy cost from node " + start + " to node " +  end + ": " + df.format(endNode.energyCost));
	    System.out.println("Shortest Path from node " + start + " to node " +  end);
		String path = Graph.buildPathStartToEnd(endNode);
		System.out.println(path);
		
		
	}
	
	//UCS or Dijkstra
	private static Node uniformCostSearch(Map<String,Node> graph,Map<String, Map<String, Double>> distWeightMap,
			Map<String, Map<String, Double>> energyWeightMap,String start,String end,double energyBudget) {
	    PriorityQueue<Node> pq = new PriorityQueue<>(new Comparator<Node>() {
			@Override
			public int compare(Node node1, Node node2) {
				int result =  (int) (node1.distCost - node2.distCost);
				if(result != 0) {
					return result;
				}
				else {
					return (int)(node1.energyCost - node2.energyCost);
				}
			}
		});

	    /*
	     * Modified UCS we allow multiple visit to the same code
	     * to find optimal distance cost and within energy budget
	     * 
	     */
	    Map<String, List<EdgeCosts>>visited = new HashMap<>();
	    //Map<String,Double> distCost = new HashMap<>();
	    //Map<String,Double> energyCost = new HashMap<>();
	   
	    Node startNode = graph.get(start);
	    pq.add(startNode);
	    
	    /*
	    * start node so far travel 0 distance and use 0 energy
	    * Each node will have a key-value pair map to an ArrayList of EdgeCosts
	    * To potentially allow alternative path from curNode to get optimal distance and within energy budget
	    */
	    visited.put(startNode.id, new ArrayList<EdgeCosts>());
	    visited.get(startNode.id).add(new EdgeCosts(0.0, 0.0)); 
	    
	    //distCost.put(startNode.id, 0.0);
	    //energyCost.put(startNode.id, 0.0);
	    
	    
	    while(!pq.isEmpty()) {
	    	/*
	    	 * Do UCS normally but we do not keep track of which node visited(relaxed) as could try again from visited node an alternate path
	    	 * Assume can allow re-visit to a node,as could have better path-energy cost
	    	*/
	    	Node curNode = pq.poll();
	    	//System.out.println("CurNode " + curNode.id);
	    	
	    	if(curNode.id.equals(end) && curNode.energyCost <= energyBudget) {
	    		//found end node already no point traverse 
	    		//System.out.println("end");
	    		return curNode;
	    	}


	    	//get all the neighbors of currentNode
	    	for(String neighborNodeID : distWeightMap.get(curNode.id).keySet()) {
	    		
	    		//cost from startNode to given neighbor node
	    		Double newDistCost = curNode.distCost + distWeightMap.get(curNode.id).get(neighborNodeID);
	    		Double newEnergyCost = curNode.energyCost + energyWeightMap.get(curNode.id).get(neighborNodeID);
	    		//create and edgeCost from (startNode to CurNode) + a potential neighbor 
	    		EdgeCosts newEdgeCost = new EdgeCosts(newDistCost ,newEnergyCost);
	    		//System.out.println("newEnergyCost " + newEnergyCost);
	    		
	    		
	    		//cancel 1->2->1
	    		if(curNode.parent != null && curNode.parent.id.equals(neighborNodeID)) {
	    			//System.out.println("go back cancel");
	    			continue;
	    		}
	    		
	    		/*
	    		 * add potential edgePath to PQ if
	    		 * within energy budget constraint and
	    		 * there is no better path to reach from (Start to curNode) + neighbor
	    		 * even if graph by-directional going backwards will make it worst 1->2->1->3 so it is taken care off also
	    		*/
	    		if(newEnergyCost <= energyBudget && 
	    				checkIfCan(newEdgeCost,visited.getOrDefault(neighborNodeID,new ArrayList<>()))) {
	    			
	    			//first time to initialize the ArrayList
	    			//putIfAbsent as we do not want to use put to overwrite the key,value pair
	    			visited.putIfAbsent(neighborNodeID, new ArrayList<>());  			
	    			//found a path or better path to reach from startNode to neighboutNode
	    			visited.get(neighborNodeID).add(newEdgeCost);
	    			//Found a path or better Path from source to neighborNode
	    			//nextNode is a potential better path from source to that node then whatever in PQ
	    			Node nextNode = new Node(neighborNodeID);
	    			nextNode.distCost = newDistCost;
	    			nextNode.energyCost = newEnergyCost;
	    			pq.add(nextNode);
	    			
	    			//keep track of parent so can construct the path from start to end
	    			//update Node if found a better path/parent to it from startNode
	    			nextNode.parent = curNode;		
	    		}
	    	}   	
	    }
	    return null;
	}
	/*
	 * edgeCost from (startNode to CurNode) + a potential neighbor 
	 * check if the newEdgeCosts to reach neighborNode obtain is lower than another path result obtain earlier to reach neighborNode
	 * if so add this newEdgeCosts to the PQ as long there is 1 path better.
	 */
	private static boolean checkIfCan(EdgeCosts newEdgeCosts,List<EdgeCosts> exploredEdges) {
		for(EdgeCosts nEdgeCost : exploredEdges) {
			if(!foundBtrpath(newEdgeCosts, nEdgeCost)) {
				return false;
			}
		}
		return true;
	}
	
	private static boolean foundBtrpath(EdgeCosts newEdgeCosts, EdgeCosts exploredEdgeCost) {
			
		return newEdgeCosts.distEdgeCost < exploredEdgeCost.distEdgeCost || newEdgeCosts.energyEdgeCost < exploredEdgeCost.energyEdgeCost;
	}
}
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from gurobipy import *
from utils.hours import hours
from utils.printMsg import printMsg

class Solution:
    pass  # Implement Scenario class if needed
    
def generate_plan(expectedDuration, scenario):
    
    printMsg(">> Generating Problem")
    
    # Ensure expectedDuration is integers
    expectedDuration = np.round(expectedDuration)

    # Settings and costs
    N = scenario.N
    vI = scenario.numInstallationVessels

    benefit = scenario.benefitForFinishingAnOWT
    benefitEarly = scenario.maxBenefitForFinishingEarly
    modV = 0.05 * np.arange(vI)
    
    # ###############################
    # ### Optimizer and Variables ###
    # ###############################
    model = gp.Model("OWT_Planning")
    
    location = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=1, name="location")
    capacity = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, name="capacity")
    xOWT = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=1, name="xOWT")
    xPortOp = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=1, name="xPortOp")
    xToPort = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=1, name="xToPort")
    xToSite = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=1, name="xToSite")
    xBusy = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=1, name="xBusy")
    xPortOpD = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=1, name="xPortOpD")
    xOWT_TimeFinished = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=scenario.N-1, name="xOWT_TimeFinished")
    xMinorOps_TimeFinished = model.addVars(vI, N, vtype=GRB.INTEGER, lb=0, ub=scenario.N-1, name="xMinorOps_TimeFinished")
    
    xPortRestockOp = model.addVars(N, vtype=GRB.INTEGER, lb=0, ub=1, name="xPortRestockOp")
    xPortCapacity = model.addVars(N, vtype=GRB.INTEGER, lb=0, ub=scenario.maximumPortCapacity, name="xPortCapacity")
    cost = model.addVar(vtype=GRB.CONTINUOUS, name="cost")
    
    # ###############################
    # ###      Cost Function      ###
    # ###############################
    dur_Movement = scenario.opData[0,6];
    
    model.addConstr(
        cost >= gp.quicksum(location[v, k] * (scenario.costOffshore + modV[v]) for v in range(vI) for k in range(N)) +
        gp.quicksum(xPortOpD[v, k] * (scenario.costPortOp + modV[v]) for v in range(vI) for k in range(N)) +
        gp.quicksum(xToSite[v, k] * (scenario.costFuel * dur_Movement + modV[v]) for v in range(vI) for k in range(N)) +
        gp.quicksum(xToPort[v, k] * (scenario.costFuel * dur_Movement + modV[v]) for v in range(vI) for k in range(N)) +
        (gp.quicksum(xPortCapacity[k] for k in range(N)) / (N * scenario.maximumPortCapacity)) * scenario.storagePenalty -
        gp.quicksum(xOWT[v, k] * benefit for v in range(vI) for k in range(N)) -
        gp.quicksum((N - xOWT_TimeFinished[v, k]) / (N * benefitEarly) for k in range(N) for v in range(vI)) -
        gp.quicksum(gp.quicksum((N - xOWT_TimeFinished[v, k]) / N for k in range(N)) * benefitEarly for v in range(vI))-
        gp.quicksum((N - xMinorOps_TimeFinished[v, k]) / N * ((benefitEarly * 0.2) / N / 84) for v in range(vI) for k in range(N)) +
        gp.quicksum(xPortOpD[v, k] for v in range(vI) for k in range(N)) * 0.01, name="constr_cost" 
        )

    # Set up the objective function
    model.setObjective(
        cost,
        GRB.MINIMIZE
        )
    
    # ### Constraints: Vessel Capactiy
    printMsg(">>> Constraint: Capacity (2)");
    model.addConstrs((capacity[v, k] <= scenario.maxShipCapacities[v] for v in range(vI) for k in range(N)),
                     name="constr_capacityMax")
    model.addConstrs((capacity[v, k] == capacity[v, k - 1] - xOWT[v, k] + xPortOp[v, k] if k > 0 else
                     capacity[v, k] == scenario.currentCapacity[v] - xOWT[v, k] + xPortOp[v, k]
                     for v in range(vI) for k in range(N)), name="constr_capacity")

    # ### Constraints: Single Job
    printMsg(">>> Constraint: Single Job (1)");
    model.addConstrs((xOWT[v, k] + xToPort[v, k] + xToSite[v, k] + xPortOp[v, k] + xBusy[v, k] <= 1
                      for v in range(vI) for k in range(N)), name="constr_oneJob")
    
    # Record Build times
    printMsg(">>> Constraint: BuildTimes (2)");
    model.addConstrs((xOWT_TimeFinished[v, k] == xOWT[v, k] * (k + expectedDuration[0, k] - 1)
                      for v in range(vI) for k in range(N)), name="constr_finishTimes")
    model.addConstrs((
        xMinorOps_TimeFinished[v, k] == xPortOp[v, k] * (k + expectedDuration[3, k] - 1) +
        xToPort[v, k] * (k + expectedDuration[2, k] - 1) +
        xToSite[v, k] * (k + expectedDuration[1, k] - 1)
        for v in range(vI) for k in range(N)), name="constr_finishOps")
    
    # Define location
    printMsg(">>> Constraint: Location (3)");
    model.addConstrs((location[v, k] == location[v, k - 1] - (xToPort[v, k]) + xToSite[v, k] if k > 0 else
                                      location[v, k] == scenario.currentLocation[v] - xToPort[v, k] + xToSite[v, k]
                                      for v in range(vI) for k in range(N)), name="constr_location1")
    model.addConstrs((location[v, k] >= xOWT[v, k] for v in range(vI) for k in range(N)),
                                      name="constr_location2")
    model.addConstrs((location[v, k] <= (1 - xPortOp[v, k]) for v in range(vI) for k in range(N)),
                                      name="constr_location3")
    
    # Dont build more than reuqired / allowed
    printMsg(">>> Constraint: Max OWTs to build (1)");
    model.addConstr(gp.quicksum(xOWT[v, k] for v in range(vI) for k in range(N)) <= scenario.OWTsToBuild - scenario.BuiltOWTs,
                                    name="constr_maxOWT")
   
    # Durations
    printMsg(">>> Constraint: Duration/Busy and Duration PortOperations (5)");
    
    for v  in range(vI):
        for k  in range(N):
            t_owt  = int(expectedDuration[0,k]) - 1
            t_move = int(expectedDuration[1,k]) - 1
            t_port = int(expectedDuration[3,k]) - 1

            k2_owt_s   = k+1
            k2_move_s  = k+1
            k2_port_s  = k+1
            k2_portD_s = k
            
            k2_owt_e  =  min(k+1+t_owt,  N);
            k2_move_e  = min(k+1+t_move, N);
            k2_port_e  = min(k+1+t_port, N);
            k2_portD_e = min(k+1+t_port, N);

            model.addConstr(xOWT[v, k] <= max(0, (N - k) - (t_owt- 1)), 
                            name=f"constr_finish[{v},{k}]")


            model.addConstr( gp.quicksum(xBusy[v, n] for n in range(k2_owt_s, k2_owt_e)) >= 
                            xOWT[v, k] * t_owt,
                            name=f"constr_duration_owt[{v},{k}]")
            
            model.addConstr( gp.quicksum(xBusy[v, n] for n in range(k2_move_s, k2_move_e)) >= 
                            (xToPort[v, k] * t_move) + (xToSite[v, k] * t_move),
                            name=f"constr_duration_move[{v},{k}]")
            
            model.addConstr( gp.quicksum(xBusy[v, n] for n in range(k2_port_s, k2_port_e)) >= 
                            (xPortOp[v, k] * t_port),
                            name=f"constr_duration_port[{v},{k}]")
            model.addConstr( gp.quicksum(xPortOpD[v, n] for n in range(k2_portD_s, k2_portD_e)) >= 
                            (xPortOp[v, k] * t_port+1),
                            name=f"constr_durationPort_port[{v},{k}]")

    # Do not plan vessels which have not yet started

    
    
    
    model.write("model_python.lp")
    model.optimize()
    
    solution = Solution()
    solution.location = np.zeros((vI, N))
    solution.capacity = np.zeros((vI, N))
    solution.xOWT = np.zeros((vI, N))
    solution.xToPort = np.zeros((vI, N))
    solution.xToSite = np.zeros((vI, N))
    for i in range(vI):
        for j in range(N):
            solution.location[i, j] = location[i, j].x
            solution.capacity[i, j] = capacity[i, j].x
            solution.xOWT[i, j] = xOWT[i, j].x
            solution.xToPort[i, j] = xToPort[i, j].x
            solution.xToSite[i, j] = xToSite[i, j].x
            # Store values for other variables as well


    solution.xPortRestockOp = np.zeros(N)
    solution.xPortCapacity = np.zeros(N)
    for j in range(N):
        xPortRestockOp[j] = xPortRestockOp[j].x
        xPortCapacity[j] = xPortCapacity[j].x

    solution.cost = cost.x
    
    print("TEST PRINT")